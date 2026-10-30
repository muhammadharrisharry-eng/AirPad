@echo off
title AirPad
cd /d "%~dp0"
set PY=
py -3 --version >nul 2>nul && set PY=py -3
if not defined PY python --version >nul 2>nul && set PY=python
if not defined PY (
  echo Python 3 was not found on this laptop.
  echo Install it from python.org and tick "Add python.exe to PATH", then run start.bat again.
  start https://www.python.org/downloads/
  pause
  exit /b
)
if not exist .fw_done (
  echo Allowing AirPad through Windows Firewall. Click YES on the next prompt.
  powershell -NoProfile -Command "Start-Process cmd -Verb RunAs -ArgumentList '/c netsh advfirewall firewall add rule name=AirPad dir=in action=allow protocol=TCP localport=8765-8775 profile=any'" && echo done> .fw_done
)
%PY% server.py
echo.
echo AirPad stopped. The message above shows the reason.
pause
