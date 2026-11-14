@echo off
cd /d "%~dp0"
py -3 webp_to_pdf.py
if errorlevel 1 python webp_to_pdf.py
