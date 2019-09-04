::
:: This script will first create a backup of the original or current hosts
:: file and save it in a file titled "hosts.skel"
::
:: If "hosts.skel" exists, the new hosts file with the customized unified hosts
:: will be copied to the proper path. Next, the DNS cache will be refreshed.
::
:: THIS BAT FILE MUST BE LAUNCHED WITH ADMINISTRATOR PRIVILEGES
:: Admin privileges script based on https://stackoverflow.com/a/10052222
::
::
@ECHO OFF
TITLE Update Hosts

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

:BackupHosts
	:: Backup default hosts file
	if not exist "%WINDIR%\System32\drivers\etc\hosts.skel" (
		COPY %WINDIR%\System32\drivers\etc\hosts %WINDIR%\System32\drivers\etc\hosts.skel
	)

:UpdateHosts
	:: Update hosts file
	python updateHostsFile.py --auto --minimise
	
	:: Move new hosts file in-place
	COPY hosts %WINDIR%\System32\drivers\etc\

	:: Flush the DNS cache
	ipconfig /flushdns
	
	:: Summary note
	pause
