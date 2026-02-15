import pymysql
from pymcprotocol import Type3E
import time
import datetime

# --- CONFIGURATION PLC ---
PLC_IP = "172.16.134.39"
PLC_PORT = 9000

# --- CONFIGURATION MYSQL ---
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = ""
MYSQL_DB = "plc_db"

def main():
    # 1. Inisialisasi PLC
    plc = Type3E()
    
    # 2. Inisialisasi Koneksi MySQL
    conn = None
    
    print("Program Sinkronisasi Sequence dimulai. Tekan Ctrl+C untuk berhenti.")
    
    while True:
        try:
            # Pastikan terhubung ke PLC
            if not plc._is_connected:
                print(f"Menghubungkan ke PLC {PLC_IP}:{PLC_PORT}...")
                plc.connect(PLC_IP, PLC_PORT)
                print("Berhasil terhubung ke PLC.")

            # Pastikan terhubung ke MySQL
            if conn is None or not conn.open:
                conn = pymysql.connect(
                    host=MYSQL_HOST,
                    user=MYSQL_USER,
                    password=MYSQL_PASSWORD,
                    database=MYSQL_DB,
                    autocommit=True
                )
            
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            # 3. Definisikan Group Pembacaan (Batch Read)
            # Membaca sekaligus 16 word per station untuk kecepatan dan stabilitas
            groups = [
                {"station_id": 3, "start": "W80", "count": 16},
                {"station_id": 12, "start": "W2C0", "count": 16},
                {"station_id": 16, "start": "W3C0", "count": 16},
            ]

            now = datetime.datetime.now()
            total_updated = 0

            for group in groups:
                try:
                    # Ambil 16 word sekaligus dalam satu permintaan ke PLC
                    data = plc.batchread_wordunits(group['start'], group['count'])
                    
                    # Update database untuk setiap nilai dalam batch
                    for i, val in enumerate(data):
                        # Kalkulasi alamat (W + hex offset)
                        start_addr_int = int(group['start'][1:], 16)
                        device_addr = f"W{hex(start_addr_int + i)[2:].upper()}"
                        
                        # Konversi ke Hex 4 digit
                        val_hex = f"{val:04X}"
                        
                        sql = "UPDATE squence SET value = %s, updated_at = %s WHERE device = %s"
                        cursor.execute(sql, (val_hex, now, device_addr))
                        total_updated += 1
                        
                except Exception as read_error:
                    print(f"Gagal membaca Group {group['start']} (ST. {group['station_id']}): {read_error}")

            print(f"[{now.strftime('%H:%M:%S')}] Berhasil sinkronisasi {total_updated} alamat.")


        except Exception as e:
            print(f"Kesalahan Utama: {e}")
            # Reset koneksi jika error
            try:
                if plc._is_connected: plc.close()
            except: pass
            try:
                if conn and conn.open: conn.close()
            except: pass
            time.sleep(3)
            continue
            
        # Delay 3 detik sesuai permintaan user
        time.sleep(3)


if __name__ == "__main__":
    main()
