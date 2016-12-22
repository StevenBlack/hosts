:: This script will create in first running backup of ORIGINAL/CURRENT hosts file in hosts.skel file.
:: If hosts.skel file exists, then NEW copy with customized unified hosts file will be copied to proper path.
:: Next DNS Cache will be refreshed.
:: YOU NEED RUNNING THIS BAT FILE IN COMMAND LINE PROMPT WITH ADMINISTRATOR PRIVILIGES
@ECHO OFF

if not exist "%WINDIR%\py.exe" (
	ECHO :: ERROR :: Python 3.5 Runtime NOT FOUND...
	ECHO :: ERROR :: Download and install lastest Python 3.5 for Windows from https://www.python.org/downloads/
	ECHO :: ERROR :: Exit...
	GOTO END
) ELSE ( 
	GOTO PY35RT
 )
:PY35RT
if not exist "%LOCALAPPDATA%\Programs\Python\Python35\Python35.dll" (
	ECHO :: ERROR :: Python 3.5 Runtime NOT FOUND...
	ECHO :: ERROR :: Download and install lastest Python 3.5 for Windows from https://www.python.org/downloads/
	ECHO :: ERROR :: Exit...
	GOTO END
) ELSE ( 
	ECHO :: INFO :: Python 3.5 Runtime was found...
	ECHO :: INFO :: Running main script...
    GOTO DNSCHECK
 )
:DNSCHECK
if not exist "%WINDIR%\System32\drivers\etc\hosts.skel" (
	COPY %WINDIR%\System32\drivers\etc\hosts %WINDIR%\System32\drivers\etc\hosts.skel
	GOTO :CLEARDNS
)
:CLEARDNS
	updateHostsFile.py -a
	COPY hosts %WINDIR%\System32\drivers\etc\
	ipconfig /flushdns
	GOTO END
:END
