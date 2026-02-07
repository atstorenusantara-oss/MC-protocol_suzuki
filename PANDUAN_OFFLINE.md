# Panduan Instalasi Offline (PLC to MySQL)

Dokumen ini menjelaskan cara memindahkan program `plc_to_mysql.py` ke komputer yang **tidak memiliki koneksi internet (Offline)**.

## 1. Persiapan (Di Komputer Online)
Saya telah mendownload library yang dibutuhkan ke folder `offline_libs`. 
Jika Anda belum melakukannya, jalankan perintah ini di komputer yang punya internet:
```powershell
mkdir offline_libs
pip download pymysql pymcprotocol -d offline_libs
```

## 2. File yang Harus Dipindahkan
Copy folder proyek ini ke Flashdisk, pastikan file berikut terbawa:
1. `plc_to_mysql.py` (Program utama)
2. `plc_db.sql` (File database)
3. Folder `offline_libs/` (Berisi file `.whl` library)
4. `install_offline.bat` (Script installer otomatis yang saya buatkan)

## 3. Instalasi di Komputer Tujuan (Offline)
Di komputer tujuan yang offline, buka folder proyek lalu jalankan file `install_offline.bat` atau jalankan perintah ini di Command Prompt:

```powershell
pip install --no-index --find-links=offline_libs pymysql pymcprotocol
```

## 4. Troubleshooting
*   **Python Belum Terinstal**: Pastikan di komputer tujuan sudah terinstal Python (minimal versi 3.8+). Jika belum, download installer `.exe` Python dari situs resminya di komputer online terlebih dahulu.
*   **MySQL/XAMPP**: Pastikan MySQL (atau XAMPP) sudah terinstal dan berjalan di komputer tujuan sebelum menjalankan program.
