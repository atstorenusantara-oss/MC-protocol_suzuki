@echo off
echo ======================================================
echo   Installing Python Libraries Offline (PLC to MySQL)
echo ======================================================
echo.

if not exist "offline_libs" (
    echo [ERROR] Folder offline_libs tidak ditemukan!
    echo Pastikan Anda sudah mengunduh library di komputer online.
    pause
    exit /b
)

echo Menginstal PyMySQL dan pymcprotocol...
python -m pip install --no-index --find-links=offline_libs pymysql pymcprotocol

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Instalasi gagal. 
    echo Pastikan Python sudah terinstal dan terdaftar di PATH.
) else (
    echo.
    echo [SUCCESS] Library berhasil diinstal!
    echo Anda sekarang bisa menjalankan: python plc_to_mysql.py
)

echo.
pause
