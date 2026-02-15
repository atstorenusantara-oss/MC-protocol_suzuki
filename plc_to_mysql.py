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

        # Buat tabel baru untuk Mapping Error sesuai gambar
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plc_error_mapping (
                device VARCHAR(10) PRIMARY KEY,
                station_id INT,
                plc_id INT,
                value TINYINT(1) DEFAULT 0,
                error_description VARCHAR(255),
                complete_comment VARCHAR(255),
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)


        # Buat tabel baru untuk Squence sesuai gambar terbaru
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS squence (
                device VARCHAR(10) PRIMARY KEY,
                station_id INT,
                plc_id INT,
                value VARCHAR(255) DEFAULT '0',
                comment VARCHAR(255),
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)


        # Buat tabel baru untuk NG PLC
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ng_plc (
                device VARCHAR(10) PRIMARY KEY,
                station_id INT,
                plc_id INT,
                value VARCHAR(255) DEFAULT '0',
                comment VARCHAR(255),
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        # Buat tabel baru untuk Total Fault
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS total_fault (
                device VARCHAR(10) PRIMARY KEY,
                comment VARCHAR(255),
                station_id INT,
                line_name VARCHAR(255),
                value VARCHAR(255) DEFAULT '0',
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
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
    
    # Inisialisasi Koneksi MySQL di luar loop agar hemat resource
    conn = None
    
    print("Program dimulai. Tekan Ctrl+C untuk berhenti.")
    
    while True:
        try:
            # 1. Pastikan terhubung ke PLC
            if not plc._is_connected:
                print(f"Menghubungkan ke PLC {PLC_IP}:{PLC_PORT}...")
                plc.connect(PLC_IP, PLC_PORT)
                print("Berhasil terhubung ke PLC.")

            # 2. Pastikan terhubung ke MySQL
            if conn is None or not conn.open:
                print(f"Menghubungkan ke MySQL {MYSQL_HOST}...")
                conn = pymysql.connect(
                    host=MYSQL_HOST,
                    user=MYSQL_USER,
                    password=MYSQL_PASSWORD,
                    database=MYSQL_DB,
                    autocommit=True
                )
                print("Berhasil terhubung ke MySQL.")
            
            cursor = conn.cursor()

            # 3. Baca data dari PLC (B0 - B7FF = 2048 bit)
            start_address = "B0"
            count = 2048
            bits_data = plc.batchread_bitunits(start_address, count)
            
            # 4. Simpan/Update ke Database
            now = datetime.datetime.now()
            
            # Gunakan ON DUPLICATE KEY UPDATE supaya:
            # - Jika address belum ada -> INSERT
            # - Jika address sudah ada -> UPDATE
            sql = """
                INSERT INTO plc_b_relay (address, value, updated_at) 
                VALUES (%s, %s, %s) 
                ON DUPLICATE KEY UPDATE value = VALUES(value), updated_at = VALUES(updated_at)
            """
            
            # Format data: (address, value, updated_at)
            data_to_save = [(f"B{i:X}", int(val), now) for i, val in enumerate(bits_data)]
            
            cursor.executemany(sql, data_to_save)
            
            # Debug: Beri info setiap 10 detik agar tidak terlalu ramai
            if int(time.time()) % 10 == 0:
                print(f"[{now.strftime('%H:%M:%S')}] OK - Sync 2048 addresses.")
            
        except Exception as e:
            print(f"Kesalahan: {e}")
            print("Mencoba lagi dalam 2 detik...")
            
            # Tutup koneksi jika error agar bisa reconnect dengan bersih
            try:
                if plc._is_connected: plc.close()
            except: pass
            
            try:
                if conn and conn.open: conn.close()
            except: pass
            
            time.sleep(2)
            continue
            
        # Delay 500ms (0.5 detik)
        time.sleep(0.5)

if __name__ == "__main__":
    main()
