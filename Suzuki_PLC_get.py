import pymysql
from pymcprotocol import Type3E
import time
import datetime
import sys

# --- CONFIGURATION PLC ---
PLC_IP = "172.16.134.39"
PLC_PORT = 9000

# --- CONFIGURATION MYSQL ---
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = ""
MYSQL_DB = "plc_db"

# --- UPDATE INTERVAL ---
INTERVAL = 3  # detik

class SuzukiPLCGet:
    def __init__(self):
        self.plc = Type3E()
        self.db_conn = None
        # Tabel yang diminta untuk diolah
        self.tables = ['plc_error_mapping', 'squence', 'total_fault', 'ng_plc']
        self.device_cache = {}

    def log(self, message, log_type="INFO"):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now}] [{log_type}] {message}")

    def connect_db(self):
        """Memastikan koneksi ke MySQL tetap aktif."""
        try:
            if self.db_conn is None or not self.db_conn.open:
                self.db_conn = pymysql.connect(
                    host=MYSQL_HOST,
                    user=MYSQL_USER,
                    password=MYSQL_PASSWORD,
                    database=MYSQL_DB,
                    autocommit=True
                )
                self.log("Terhubung ke MySQL Database.")
            return True
        except Exception as e:
            self.log(f"Gagal terhubung ke MySQL: {e}", "ERROR")
            self.db_conn = None
            return False

    def connect_plc(self):
        """Memastikan koneksi ke PLC tetap aktif."""
        try:
            if not self.plc._is_connected:
                self.log(f"Menghubungkan ke PLC {PLC_IP}:{PLC_PORT}...")
                self.plc.connect(PLC_IP, PLC_PORT)
                self.log("Berhasil terhubung ke PLC.")
            return True
        except Exception as e:
            self.log(f"Gagal terhubung ke PLC: {e}", "ERROR")
            return False

    def refresh_device_list(self):
        """Mengambil daftar alamat (device) dari semua tabel target di Database."""
        if not self.connect_db():
            return False
        
        try:
            cursor = self.db_conn.cursor()
            new_cache = {}
            total_count = 0
            
            for table in self.tables:
                # Mengambil kolom 'device' sesuai permintaan
                cursor.execute(f"SELECT device FROM {table}")
                rows = cursor.fetchall()
                new_cache[table] = [row[0] for row in rows]
                total_count += len(rows)
            
            self.device_cache = new_cache
            return True
        except Exception as e:
            self.log(f"Gagal memuat daftar device dari database: {e}", "ERROR")
            return False

    def get_plc_value(self, device, count=1):
        """Membaca nilai dari PLC berdasarkan alamat (B, W, M, D, dll)."""
        try:
            # Deteksi tipe device berdasarkan prefix
            prefix = device[0].upper()
            
            if prefix in ['B', 'M', 'X', 'Y']:
                # Baca sebagai Bit (returns 0 or 1)
                results = self.plc.batchread_bitunits(device, count)
                return results if count > 1 else results[0]
            else:
                # Baca sebagai Word (returns integer value)
                results = self.plc.batchread_wordunits(device, count)
                return results if count > 1 else results[0]
        except Exception as e:
            # Jika gagal baca, kemungkinan koneksi putus
            self.log(f"Gagal membaca device {device}: {e}", "DEBUG")
            try:
                self.plc.close()
            except:
                pass
            return None

    def update_db_value(self, table, device, value):
        """Memperbarui kolom value di database untuk device tertentu."""
        try:
            cursor = self.db_conn.cursor()
            # Update kolom 'value' dan 'updated_at'
            sql = f"UPDATE {table} SET value = %s, updated_at = NOW() WHERE device = %s"
            cursor.execute(sql, (str(value), device))
        except Exception as e:
            self.log(f"Gagal update database pada tabel {table}, device {device}: {e}", "ERROR")

    def run(self):
        """Loop utama program."""
        print("="*60)
        print("          SUZUKI PLC DATA ACQUISITION SYSTEM          ")
        print(f"       Mode: Continuous Update (Every {INTERVAL}s)       ")
        print("="*60)
        
        while True:
            start_run = time.time()
            
            # 1. Pastikan koneksi OK
            plc_ready = self.connect_plc()
            db_ready = self.connect_db()
            
            if plc_ready and db_ready:
                # 2. Refresh daftar device (agar dinamis jika isi tabel berubah)
                if self.refresh_device_list():
                    total_updated = 0
                    
                    # 3. Proses setiap tabel dan device-nya
                    for table, devices in self.device_cache.items():
                        for device in devices:
                            # Khusus 'squence' baca 2 word (32-bit/Double Word)
                            read_count = 2 if table == 'squence' else 1
                            val = self.get_plc_value(device, read_count)
                            
                            if val is not None:
                                if table == 'squence':
                                    # Menggabungkan 2 word sebagai ASCII (misal 2 register '16' dan '45' -> "1645")
                                    # Kemudian dikonversi ke Desimal integer
                                    try:
                                        ascii_str = ""
                                        # Mitsubishi: 1 Word = 2 Karakter ASCII
                                        for word_val in val:
                                            low_char = chr(word_val & 0xFF)
                                            high_char = chr((word_val >> 8) & 0xFF)
                                            ascii_str += low_char + high_char
                                        
                                        # Hilangkan karakter null atau spasi jika ada di akhir
                                        ascii_str = ascii_str.strip('\x00').strip()
                                        
                                        # Konversi ke Desimal (contoh: "1645" -> 1645)
                                        val_to_save = int(ascii_str)
                                    except (ValueError, TypeError):
                                        # Fallback jika bukan angka: simpan sebagai string hex gabungan
                                        val_to_save = "".join([f"{v:04X}" for v in val])
                                else:
                                    val_to_save = val
                                
                                self.update_db_value(table, device, val_to_save)
                                total_updated += 1
                    
                    if total_updated > 0:
                        self.log(f"Berhasil sinkronisasi {total_updated} alamat dari PLC ke Database.")
                else:
                    self.log("Daftar device kosong atau gagal dimuat.", "WARNING")
            else:
                self.log("Menunggu koneksi PLC/Database pulih...", "WAIT")
            
            # 4. Timer interval
            elapsed = time.time() - start_run
            sleep_time = max(0, INTERVAL - elapsed)
            time.sleep(sleep_time)

if __name__ == "__main__":
    app = SuzukiPLCGet()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nProgram dihentikan oleh pengguna.")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal Error: {e}")
        sys.exit(1)
