@echo off
cd /d "%~dp0"
set PY=python
py -3 --version >nul 2>nul && set PY=py -3
set "V=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\AirPad.vbs"
> "%V%" echo Set s=CreateObject("WScript.Shell"):s.CurrentDirectory="%~dp0":s.Run "cmd /c %PY% server.py --quiet",0
echo AirPad will now start by itself (hidden) every time Windows starts.
echo To pair a new phone, open http://localhost:8765/pair on this laptop.
pause
