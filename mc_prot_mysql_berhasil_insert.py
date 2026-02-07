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
    
    try:
        # Hubungkan ke PLC
        print(f"Menghubungkan ke PLC {PLC_IP}:{PLC_PORT}...")
        plc.connect(PLC_IP, PLC_PORT)
        print("Berhasil terhubung ke PLC.")

        # Range B0 sampai B7FF (0x0 sampai 0x7FF)
        # Total ada 2048 bit (0x800)
        start_address = "B0"
        count = 2048
        
        # Baca data dari PLC
        print(f"Membaca {count} bit mulai dari {start_address}...")
        bits_data = plc.batchread_bitunits(start_address, count)
        
        # Persiapkan data untuk MySQL
        now = datetime.datetime.now()
        data_to_save = []
        
        for i, val in enumerate(bits_data):
            # Format alamat kembali ke Hex (B0, B1, ..., B7FF)
            addr_str = f"B{i:X}"
            # Pastikan nilai adalah integer (0 atau 1)
            bit_val = int(val)
            # Masukkan data (address, value, updated_at, value_update, timestamp_update)
            data_to_save.append((addr_str, bit_val, now, bit_val, now))

        # Simpan ke Database
        conn = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            autocommit=True
        )
        cursor = conn.cursor()
        
        # Menggunakan INSERT ON DUPLICATE KEY UPDATE agar bisa menangani data baru maupun update
        sql = """
            INSERT INTO plc_b_relay (address, value, updated_at) 
            VALUES (%s, %s, %s) 
            ON DUPLICATE KEY UPDATE value = VALUES(value), updated_at = VALUES(updated_at)
        """
        
        print("Menyimpan data ke MySQL (Insert/Update)...")
        # Format data: (address, value, updated_at)
        data_to_save = [(f"B{i:X}", int(val), now) for i, val in enumerate(bits_data)]
        
        cursor.executemany(sql, data_to_save)
        print(f"Berhasil menyimpan {len(data_to_save)} data ke MySQL.")
        
    except Exception as e:
        print(f"Kesalahan: {e}")
    finally:
        plc.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
