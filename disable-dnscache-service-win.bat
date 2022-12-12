@echo off
setlocal
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
    call :UACPrompt
) else (
    call :gotAdmin
)

exit /b 0


:UACPrompt
    set "output_file=%TEMP%\getadmin.vbs"
    echo Set UAC = CreateObject^("Shell.Application"^) > "%output_file%"
    set params= %*
    echo UAC.ShellExecute "cmd.exe", "/c ""%~s0"" %params:"=""%", "", "runas", 1 >> "%output_file%"

    wscript.exe "%output_file%"
    del "%output_file%"
exit /b

:gotAdmin
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
exit /b 0
