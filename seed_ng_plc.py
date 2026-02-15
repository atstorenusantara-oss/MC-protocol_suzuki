import pymysql

# --- CONFIGURATION MYSQL ---
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = ""
MYSQL_DB = "plc_db"

def seed_ng_plc():
    try:
        conn = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            autocommit=True
        )
        cursor = conn.cursor()

        # Bersihkan tabel sebelum memasukkan data baru
        cursor.execute("TRUNCATE TABLE ng_plc")
        print("Tabel ng_plc telah dibersihkan.")

        # Data Station 3: W90 - W9F
        # Data Station 12: W2D0 - W2DF
        # Data Station 16: W3D0 - W3DF
        data_to_insert = []
        
        # Insert Station 3
        for i in range(16):
            device = f"W{0x90 + i:X}"
            plc_id = i + 1  # 1-16
            station_id = 3
            value = "0"
            comment = f"PCB<-3 OK/NG STATION {plc_id}"
            data_to_insert.append((device, station_id, plc_id, value, comment))

        # Insert Station 12
        for i in range(16):
            device = f"W{0x2D0 + i:X}"
            plc_id = i + 1  # 1-16
            station_id = 12
            value = "0"
            comment = f"PCB<-12 OK/NG STATION {plc_id}"
            data_to_insert.append((device, station_id, plc_id, value, comment))

        # Insert Station 16
        for i in range(16):
            device = f"W{0x3D0 + i:X}"
            plc_id = i + 1  # 1-16
            station_id = 16
            value = "0"
            comment = f"PCB<-16 OK/NG STATION {plc_id}"
            data_to_insert.append((device, station_id, plc_id, value, comment))


        sql = """
            INSERT INTO ng_plc (device, station_id, plc_id, value, comment)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                station_id = VALUES(station_id),
                plc_id = VALUES(plc_id),
                value = VALUES(value),
                comment = VALUES(comment)
        """

        cursor.executemany(sql, data_to_insert)
        print(f"Berhasil memasukkan {len(data_to_insert)} data NG PLC (Bernilai Awal) ke database.")
        
        conn.close()
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    seed_ng_plc()
