@echo off

title Disable DNS Cache Service

:: Check if we are an administrator. If not, exit immediately.
:: BatchGotAdmin
:: Check for permissions
if "%PROCESSOR_ARCHITECTURE%" equ "amd64" (
  >nul 2>&1 "%SYSTEMROOT%\SysWOW64\cacls.exe" "%SYSTEMROOT%\SysWOW64\config\system"
) else (
  >nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
)

:: If the error flag set, we do not have admin rights.
if %ERRORLEVEL% neq 0 (
  echo Requesting administrative privileges...
  goto UACPrompt
) else (
  goto gotAdmin
)

:UACPrompt
echo Set UAC = CreateObject^("Shell.Application"^) > "%TEMP%\getadmin.vbs"
set params= %*
echo UAC.ShellExecute "cmd.exe", "/c ""%~s0"" %params:"=""%", "", "runas", 1 >> "%TEMP%\getadmin.vbs"

wscript.exe "%TEMP%\getadmin.vbs"
del "%TEMP%\getadmin.vbs"
exit /b

:gotAdmin

:SCset
:: VALUE
:: 2 (Automatic) (DEFAULT)
:: 4 (Disabled) (to prevent network freeze after applying a huge hosts file)
::
:: See https://superuser.com/a/1277960
::
reg add "HKLM\SYSTEM\CurrentControlSet\services\Dnscache" /v Start /t REG_DWORD /d 4 /f
echo Reboot your system now!
echo.
pause
