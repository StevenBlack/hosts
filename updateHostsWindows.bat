::
:: This script will first create a backup of the original or the current hosts
:: file and save it in a file named "hosts.skel".
::
:: If the "hosts.skel" file exists, the new hosts file with the customized unified
:: hosts will be copied to the proper path. Next, the DNS cache will be refreshed.
::
:: THIS BAT FILE MUST BE LAUNCHED WITH ADMINISTRATOR PRIVILEGES
:: Admin privileges script based on https://stackoverflow.com/a/10052222
::

@echo off
setlocal
title Update Hosts

set "calcs_executable=%SYSTEMROOT%\SysWOW64\cacls.exe"
set "calcs_file=%SYSTEMROOT%\system32\config\system"

:: Check if we are an administrator. If not, exit immediately.
:: BatchGotAdmin
:: Check for permissions
if "%PROCESSOR_ARCHITECTURE%" equ "amd64" (
    >nul 2>&1 "%calcs_executable%" "%calcs_file%"
) else (
    >nul 2>&1 "%calcs_executable%" "%calcs_file%"
)

:: Summary note
pause
exit /b 0


:: If the error flag set, we do not have admin rights.
if %ERRORLEVEL% neq 0 (
    echo Requesting administrative privileges...
    call :UACPrompt
) else (
    call :gotAdmin
)

:UACPrompt
    set "output_file=%TEMP%\getadmin.vbs"
    echo Set UAC = CreateObject^("Shell.Application"^) > "%output_file%"
    set params= %*
    echo UAC.ShellExecute "cmd.exe", "/c ""%~s0"" %params:"=""%", "", "runas", 1 >> "%output_file%"

    wscript.exe "%output_file%"
    del "%output_file%"
exit /b 0

:gotAdmin
    cd /d "%~dp0"

    set "common_prefix=%WINDIR%\System32\drivers\etc\hosts"
    :: Backup the default hosts file
    if not exist "%common_prefix%.skel" (
        copy /v "%common_prefix%" "%common_prefix%.skel"
    )

    :: Update hosts file
    py updateHostsFile.py --auto --minimise %*

    :: Copy over the new hosts file in-place
    copy /y /v hosts "%WINDIR%\System32\drivers\etc\"

    :: Flush the DNS cache
    ipconfig /flushdns
exit /b 0
