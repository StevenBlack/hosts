:: This script will create in first running backup of ORIGINAL/CURRENT hosts file in hosts.skel file.
:: If hosts.skel file exists, then NEW copy with customized unified hosts file will be copied to proper path.
:: Next DNS Cache will be refreshed.
:: THIS BAT FILE WILL BE LAUNCHED WITH ADMINISTRATOR PRIVILEGES
@ECHO OFF
SETLOCAL EnableDelayedExpansion
TITLE Update Hosts

VER | FINDSTR /L "5.1." > NUL
IF %ERRORLEVEL% EQU 0 GOTO START

VER | FINDSTR /L "5.2." > NUL
IF %ERRORLEVEL% EQU 0 GOTO START

CLS
IF "%1"=="" GOTO CHECK_UAC
IF "%1"=="start" GOTO START

:CHECK_UAC
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"  
If '%ERRORLEVEL%' NEQ '0' (
    ECHO Requesting administrative privileges...
    GOTO UAC_PROMPT
) Else (
    GOTO ADMIN
)

:UAC_PROMPT
ECHO Set UAC = CreateObject^("Shell.Application"^) > "%TEMP%\getadmin.vbs"
ECHO UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%TEMP%\getadmin.vbs"
"%TEMP%\getadmin.vbs"
EXIT /B

:ADMIN
IF EXIST "%TEMP%\getadmin.vbs" ( DEL "%TEMP%\getadmin.vbs" )
PUSHD "%CD%"
CD /D "%~dp0"
CD %CD%
%COMSPEC% /c "updateHostsWindows.bat" start
EXIT

:START
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
ENDLOCAL
