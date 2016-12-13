#!/bin/bash
# This script will create in first running backup of ORIGINAL/CURRENT hosts file in hosts.skel file.
# If hosts.skel file exists, then NEW copy with customized unified hosts file will be copied to proper path.
# Next DNS Cache will be refreshed.
# YOU NEED RUNNING THIS BAT FILE IN COMMAND LINE PROMPT WITH ADMINISTRATOR PRIVILIGES
# sudo ./updaeHosts.sh

function updateHosts {
	echo "* * * Updating hosts * * *"
	python updateHostsFile.py -a >> /dev/null
	echo "* * * Copying hosts to /etc/hosts * * *"
	cp hosts /etc/hosts
}

if [ -e "/etc/hosts.skel" ]
then
	updateHosts
else
	echo "* * * Creating a Backup of current hosts file (/etc/hosts.skel) * * *"
	cp /etc/hosts /etc/hosts.skel
	updateHosts
fi
