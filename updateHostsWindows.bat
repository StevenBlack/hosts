:: This script will create in first running backup of ORIGINAL/CURRENT
:: hosts file in hosts.skel file.
::
:: If hosts.skel file exists, then the NEW copy with customized unified hosts
:: file will be copied to proper path. Next, the DNS Cache will be refreshed.
::
:: THIS BAT FILE MUST BE LAUNCHED WITH ADMINISTRATOR PRIVILEGES
@ECHO OFF
TITLE Update Hosts

:: Check if we are administrator. If not, exit immediately.
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if %ERRORLEVEL% NEQ 0 (
    ECHO This script must be run with administrator privileges!
    ECHO Please launch command prompt as administrator. Exiting...
    EXIT /B 1
)

if not exist "%WINDIR%\System32\drivers\etc\hosts.skel" (
	COPY %WINDIR%\System32\drivers\etc\hosts %WINDIR%\System32\drivers\etc\hosts.skel
)

:: Update hosts file
python updateHostsFile.py -a

:: Move new hosts file in-place
COPY hosts %WINDIR%\System32\drivers\etc\

:: Flush the DNS cache
ipconfig /flushdns
