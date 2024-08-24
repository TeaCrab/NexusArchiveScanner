@echo off
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "DATE=%dt:~0,4%%dt:~4,2%%dt:~6,2%"
set "TIME=%dt:~8,2%%dt:~10,2%%dt:~12,2%"

pip install -r requirements.txt

pause