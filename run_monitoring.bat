@echo off
title PLC Monitoring Service
:: Mengarahkan lokasi ke folder tempat script berada
cd /d "%~dp0"

echo ======================================================
echo   Starting PLC to MySQL Monitoring Service
echo   Interval: 500ms
echo ======================================================
echo.

:loop
:: Jalankan program python
python plc_to_mysql.py

:: Jika program berhenti/crash karena error, tunggu 5 detik lalu restart otomatis
echo.
echo [WARNING] Program terhenti. Restarting dalam 5 detik...
timeout /t 5
goto loop
