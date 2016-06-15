:: This script will create in first running backup of ORIGINAL/CURRENT hosts file in hosts.skel file.
:: If hosts.skel file exists, then NEW copy with customized unified hosts file will be copied to proper path.
:: Next DNS Cache will be refreshed.
:: YOU NEED RUNNING THIS BAT FILE IN COMMAND LINE PROMPT WITH ADMINISTRATOR PRIVILIGES
@ECHO OFF
if not exist "%WINDIR%\System32\drivers\etc\hosts.skel" (
	COPY %WINDIR%\System32\drivers\etc\hosts %WINDIR%\System32\drivers\etc\hosts.skel
	GOTO :CLEARDNS
)
:CLEARDNS
	COPY hosts %WINDIR%\System32\drivers\etc\
	ipconfig /flushdns
	GOTO END
:END