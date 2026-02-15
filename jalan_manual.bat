@echo off
title Manual Run: Suzuki PLC Get
:: Mengarahkan lokasi ke folder tempat script berada
cd /d "%~dp0"

echo ======================================================
echo   RUNNING SUZUKI PLC DATA ACQUISITION (MANUAL)
echo ======================================================
echo.

:: Menjalankan program python
python Suzuki_PLC_get.py

echo.
echo ======================================================
echo   PROGRAM SELESAI / TERHENTI
echo ======================================================
pause
