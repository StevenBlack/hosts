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
if not exist "%PROGRAMFILES%\python35\Python35.dll" (
	ECHO :: ERROR :: Python 3.5 Runtime NOT FOUND...
	ECHO :: ERROR :: Download and install lastest Python 3.5 for Windows from https://www.python.org/downloads/
	ECHO :: ERROR :: Exit...
	GOTO END
) ELSE ( 
	ECHO :: INFO :: Python 3.5 Runtime was found!
	ECHO :: INFO :: Running main script...
	GOTO :UPDATES
 )
:UPDATES
	::These create various alternate hosts files by combining and adding the gambling, porn, and social media extensions.
	updateHostsFile.py -a    -o alternates\gambling -e gambling
	updateHostsFile.py -a -n -o alternates\porn -e porn
	updateHostsFile.py -a -n -o alternates\social -e social
	updateHostsFile.py -a -n -o alternates\gambling-porn -e gambling porn
	updateHostsFile.py -a -n -o alternates\gambling-social -e gambling social
	updateHostsFile.py -a -n -o alternates\porn-social -e porn social
	updateHostsFile.py -a -n -o alternates\gambling-porn-social -e gambling porn social
	updateHostsFile.py -a -n

	::Update the readmes.
	updateReadme.py

	GOTO END
:END
