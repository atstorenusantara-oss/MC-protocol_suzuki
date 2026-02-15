import pymysql

# --- CONFIGURATION MYSQL ---
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = ""
MYSQL_DB = "plc_db"

def seed_sequence():
    try:
        conn = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            autocommit=True
        )
        cursor = conn.cursor()

        # Bersihkan tabel sebelum memasukkan data baru untuk membuang data lama yang salah
        cursor.execute("TRUNCATE TABLE squence")
        print("Tabel squence telah dibersihkan.")

        # Data Station 3: W80, W82, ...
        # Data Station 12: W2C0, W2C2, ...
        # Data Station 16: W3C0, W3C2, ...
        data_to_insert = []
        
        # Insert Station 3
        for i in range(16):
            # Lompat 2 (0, 2, 4, ...)
            offset = i * 2
            device = f"W{0x80 + offset:X}"
            plc_id = i + 1  # 1-16
            station_id = 3
            value = "0"
            comment = f"PCB<-3 SEQ. STATION {plc_id}"
            data_to_insert.append((device, station_id, plc_id, value, comment))

        # Insert Station 12
        for i in range(16):
            offset = i * 2
            device = f"W{0x2C0 + offset:X}"
            plc_id = i + 1  # 1-16
            station_id = 12
            value = "0"
            comment = f"PCB<-12 SEQ. STATION {plc_id}"
            data_to_insert.append((device, station_id, plc_id, value, comment))

        # Insert Station 16
        for i in range(16):
            offset = i * 2
            device = f"W{0x3C0 + offset:X}"
            plc_id = i + 1  # 1-16
            station_id = 16
            value = "0"
            comment = f"PCB<-16 SEQ. STATION {plc_id}"
            data_to_insert.append((device, station_id, plc_id, value, comment))


        sql = """
            INSERT INTO squence (device, station_id, plc_id, value, comment)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                station_id = VALUES(station_id),
                plc_id = VALUES(plc_id),
                value = VALUES(value),
                comment = VALUES(comment)
        """

        cursor.executemany(sql, data_to_insert)
        print(f"Berhasil memasukkan {len(data_to_insert)} data sequence ke database.")
        
        conn.close()
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    seed_sequence()
