# Panduan Instalasi Offline (Suzuki PLC Monitoring)

Dokumen ini menjelaskan cara memindahkan program monitoring ke komputer yang **tidak memiliki koneksi internet (Offline)**.

## 1. Persiapan (Sudah Dilakukan)
Saya telah mendownload library yang dibutuhkan ke folder `offline_libs`. Folder tersebut sudah berisi:
*   `pymysql` (Untuk koneksi database)
*   `pymcprotocol` (Untuk komunikasi dengan PLC Mitsubishi)

## 2. File yang Harus Dipindahkan
Copy seluruh isi folder proyek ini ke Flashdisk. Pastikan file-file penting berikut terbawa:
1.  **`Suzuki_PLC_get.py`** (Program utama terbaru)
2.  **`plc_db.sql`** (Struktur database)
3.  **Folder `offline_libs/`** (Kunci instalasi offline)
4.  **`install_offline.bat`** (Script installer otomatis)
5.  **Script Seeding** (`seed_sequence.py`, `seed_ng_plc.py`, dll untuk isi data awal)

## 3. Instalasi di Komputer Tujuan (Offline)
1.  Buka folder proyek di komputer tujuan.
2.  Klik kanan pada **`install_offline.bat`** dan pilih "Run as Administrator" (jika perlu) atau cukup klik 2x.
3.  Script akan menginstal library secara otomatis tanpa menggunakan internet.

## 4. Langkah Menjalankan Pertama Kali
Setelah library terinstal:
1.  Import database `plc_db.sql` ke MySQL/XAMPP Anda.
2.  Jalankan script seed untuk mengisi daftar alamat PLC:
    ```powershell
    python seed_sequence.py
    python seed_ng_plc.py
    python seed_error_mapping.py
    python seed_total_fault.py
    ```
3.  Jalankan program utama:
    ```powershell
    python Suzuki_PLC_get.py
    ```

## 5. Troubleshooting
*   **Python Belum Terinstal**: Pastikan komputer sudah ada Python (3.8+).
*   **PIP Not Recognized**: Jika `install_offline.bat` error, pastikan Python sudah masuk ke "Environment Variables" (PATH).
