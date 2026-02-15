@echo off
set "SCRIPT_PATH=%~dp0run_monitoring.bat"
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_NAME=SuzukiPLC_Monitoring.vbs"

echo ======================================================
echo   SETUP AUTORUN FOR SUZUKI PLC MONITORING
echo ======================================================
echo.

:: Membuat file VBS sementara untuk menjalankan batch script secara tersembunyi/background 
:: agar tidak mengganggu tampilan Desktop saat startup (optional).
:: Jika Anda ingin jendela CMD tetap muncul, kita bisa ganti logikanya.
:: Namun biasanya autorun lebih baik menggunakan jendela CMD agar terlihat statusnya.

echo Membuat shortcut di folder Startup...
set "TARGET_LNK=%STARTUP_FOLDER%\SuzukiPLC_Monitoring.lnk"

powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%TARGET_LNK%');$s.TargetPath='%SCRIPT_PATH%';$s.WorkingDirectory='%~dp0';$s.Save()"

if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] Autorun berhasil dikonfigurasi!
    echo Program akan berjalan otomatis saat komputer dinyalakan.
    echo Lokasi shortcut: %TARGET_LNK%
) else (
    echo.
    echo [ERROR] Gagal membuat shortcut. Coba jalankan sebagai Administrator.
)

echo.
pause
