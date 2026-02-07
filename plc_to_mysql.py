import pymysql
from pymcprotocol import Type3E
import datetime
import time

# --- CONFIGURATION PLC ---
PLC_IP = "172.16.134.39"
PLC_PORT = 9000

# --- CONFIGURATION MYSQL ---
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = ""
MYSQL_DB = "plc_db"

def setup_database():
    """Memastikan database dan tabel sudah siap."""
    try:
        # Koneksi tanpa memilih DB dulu untuk membuat DB jika belum ada
        conn = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            autocommit=True
        )
        cursor = conn.cursor()
        
        # Buat database jika tidak ada
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DB}")
        cursor.execute(f"USE {MYSQL_DB}")
        
        # Buat tabel untuk menyimpan status relay B
        # address: Alamat PLC (B0 - B7FF)
        # value: Status (0 atau 1)
        # updated_at: Waktu pembaruan terakhir
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plc_b_relay (
                address VARCHAR(10) PRIMARY KEY,
                value TINYINT(1),
                updated_at DATETIME
            )
        """)
        conn.close()
        return True
    except Exception as e:
        print(f"Terjadi kesalahan saat setup database: {e}")
        return False

def main():
    if not setup_database():
        return

    # Inisialisasi PLC
    plc = Type3E()
    
    print("Program dimulai. Tekan Ctrl+C untuk berhenti.")
    
    while True:
        try:
            # Hubungkan ke PLC jika belum terhubung
            if not plc._is_connected:
                print(f"Menghubungkan ke PLC {PLC_IP}:{PLC_PORT}...")
                plc.connect(PLC_IP, PLC_PORT)
                print("Berhasil terhubung ke PLC.")

            # Range B0 sampai B7FF (0x0 sampai 0x7FF)
            start_address = "B0"
            count = 2048
            
            # Baca data dari PLC
            bits_data = plc.batchread_bitunits(start_address, count)
            
            # Persiapkan data untuk MySQL
            now = datetime.datetime.now()
            
            # Simpan/Update ke Database
            conn = pymysql.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DB,
                autocommit=True
            )
            cursor = conn.cursor()
            
            # Menggunakan query UPDATE
            sql = "UPDATE plc_b_relay SET value = %s, updated_at = %s WHERE address = %s"
            
            # Format data untuk UPDATE: (value, updated_at, address)
            data_to_update = [(int(val), now, f"B{i:X}") for i, val in enumerate(bits_data)]
            
            cursor.executemany(sql, data_to_update)
            conn.close()
            
            # Output status setiap pembacaan (opsional, bisa dihapus jika terlalu ramai)
            # print(f"[{now.strftime('%H:%M:%S.%f')[:-3]}] Data diperbarui.")
            
        except Exception as e:
            print(f"Kesalahan: {e}")
            print("Mencoba lagi dalam 2 detik...")
            try:
                plc.close()
            except:
                pass
            time.sleep(2)
            continue
            
        # Delay 500ms (0.5 detik)
        time.sleep(0.5)

if __name__ == "__main__":
    main()
