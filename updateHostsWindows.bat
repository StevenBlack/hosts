:: This script will first create a backup of the original or current hosts
:: file and save it in a file titled "hosts.skel"
::
:: If "hosts.skel" exists, the new hosts file with the customized unified hosts
:: will be copied to the proper path. Next, the DNS cache will be refreshed.
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
if exist updateHostsFile.exe (
    echo run exe
    updateHostsFile --auto --extensions fakenews social gambling
) else (
    echo run script
    python updateHostsFile.py --auto --extensions fakenews social gambling
)

:: Move new hosts file in-place
COPY hosts %WINDIR%\System32\drivers\etc\

:: Flush the DNS cache
ipconfig /flushdns

:endofscript