@echo off
chcp 65001 >nul
title Tu khoi dong IDC Harness
REM Tu khoi dong Javis cung Windows. Dung: idc-autostart.bat install | uninstall | status
REM Logic nam trong idc-autostart.ps1 (ghi/xoa muc JavisOS trong HKCU Run, khong can quyen
REM admin). Bat roi thi dang nhap may la server tu chay nen va tu mo dashboard (0.306.0).
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0idc-autostart.ps1" %1
