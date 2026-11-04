@echo off
chcp 65001 >nul
title Khoi dong IDC Harness
cd /d "%~dp0"

echo Bat IDC Harness chay NEN - khong con cua so den (port 7777)...
REM Viec tat instance cu + chay server AN giao het cho start-idc.vbs (cua so an hoan toan).
REM Log ghi vao server\javis.log (mo file do neu can xem loi). Tat server: stop-idc.bat.
wscript //nologo start-idc.vbs

echo.
echo Da bat. Cho ~10 giay roi mo http://localhost:7777 va bam Ctrl+Shift+R.
echo (Tat server: chay stop-idc.bat. Xem loi: mo file server\javis.log)
timeout /t 4 >nul
