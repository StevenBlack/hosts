@ECHO OFF
:: Check if we are administrator. If not, exit immediately.
:: BatchGotAdmin
:-------------------------------------
REM  --> Check for permissions
    IF "%PROCESSOR_ARCHITECTURE%" EQU "amd64" (
>nul 2>&1 "%SYSTEMROOT%\SysWOW64\cacls.exe" "%SYSTEMROOT%\SysWOW64\config\system"
) ELSE (
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
)

REM --> If error flag set, we do not have admin.
if '%errorlevel%' NEQ '0' (
    echo Requesting administrative privileges...
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    set params= %*
    echo UAC.ShellExecute "cmd.exe", "/c ""%~s0"" %params:"=""%", "", "runas", 1 >> "%temp%\getadmin.vbs"

    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    pushd "%CD%"
    CD /D "%~dp0"
    goto SCset

:SCset
:: https://superuser.com/a/1217703
:: https://stackoverflow.com/a/133926
::sc config Dnscache start= disabled
::sc stop Dnscache

:: VALUE 
:: 2 (Automatic) (DEFAULT)
:: 4 (Disabled) (prevent freeze network after applying huge hosts file)
::
:: Latest changes in security Windows 10 denied access to changing services via other tools except registry hack
::
:: See https://superuser.com/a/1277960
::
REG add "HKLM\SYSTEM\CurrentControlSet\services\Dnscache" /v Start /t REG_DWORD /d 4 /f
echo "Reboot your system now!"
echo .
@PAUSE
