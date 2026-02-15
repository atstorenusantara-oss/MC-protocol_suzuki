import pymysql

# --- CONFIGURATION MYSQL ---
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = ""
MYSQL_DB = "plc_db"

def seed_data():
    try:
        conn = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            autocommit=True
        )
        cursor = conn.cursor()

        # Data dari gambar pertama (Station 3: B154 - B163)
        devices_st3 = [f"B{i:X}" for i in range(0x154, 0x163 + 1)]
        
        # Data dari gambar kedua (Station 12: B5D4 - B5E3)
        devices_st12 = [f"B{i:X}" for i in range(0x5D4, 0x5E3 + 1)]

        # Data dari gambar ketiga (Station 16: B7D4 - B7E3)
        devices_st16 = [f"B{i:X}" for i in range(0x7D4, 0x7E3 + 1)]

        data_to_insert = []
        
        # Station 3
        for index, device in enumerate(devices_st3, start=1):
            poka_label = f"Poka0{index}"
            desc = f"{poka_label} Process Start"
            comment = f"{desc} FROM ST. 3"
            data_to_insert.append((device, 3, index, 0, desc, comment))
            
        # Station 12
        for index, device in enumerate(devices_st12, start=1):
            poka_label = f"Poka0{index}"
            desc = f"{poka_label} Process Start"
            comment = f"{desc} FROM ST. 12"
            data_to_insert.append((device, 12, index, 0, desc, comment))

        # Station 16
        for index, device in enumerate(devices_st16, start=1):
            poka_label = f"Poka0{index}"
            desc = f"{poka_label} Process Start"
            comment = f"{desc} FROM ST. 16"
            data_to_insert.append((device, 16, index, 0, desc, comment))


        sql = """
            INSERT INTO plc_error_mapping (device, station_id, plc_id, value, error_description, complete_comment)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                station_id = VALUES(station_id),
                plc_id = VALUES(plc_id),
                value = VALUES(value),
                error_description = VALUES(error_description),
                complete_comment = VALUES(complete_comment)
        """



        cursor.executemany(sql, data_to_insert)
        print(f"Berhasil memasukkan {len(data_to_insert)} data mapping error ke database.")
        
        conn.close()
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    seed_data()
