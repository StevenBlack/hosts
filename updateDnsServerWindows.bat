:: This script will create cmd file for update config for Windows DNS server 
@ECHO OFF

ECHO Creating 'dns-upd.cmd' from 'hosts' ...
powershell -command "(get-content hosts) -replace '^0.0.0.0[ \t](.*)', 'dnscmd /ZoneAdd $1 /Primary /file $1.dns' | where { $_ -match '^dnscmd' } | set-content dns-upd.cmd"

ECHO Start update DNS server config
powershell -command ".\dns-upd.cmd | set-content dns-upd.log"
