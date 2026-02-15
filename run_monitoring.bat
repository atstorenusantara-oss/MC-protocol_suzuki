@echo off
title Suzuki PLC Monitoring Service
:: Mengarahkan lokasi ke folder tempat script berada
cd /d "%~dp0"

echo ======================================================
echo   Starting Suzuki PLC Monitoring System
echo   Interval: 3 Seconds
echo ======================================================
echo.

:loop
:: Jalankan program python
python Suzuki_PLC_get.py

:: Jika program berhenti/crash karena error, tunggu 5 detik lalu restart otomatis
echo.
echo [WARNING] Program terhenti. Restarting dalam 5 detik...
timeout /t 5
goto loop
