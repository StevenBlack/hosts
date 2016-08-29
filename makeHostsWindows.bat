@ECHO OFF
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
