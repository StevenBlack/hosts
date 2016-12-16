#!/usr/bin/env bash
# This script will create in first running backup of ORIGINAL/CURRENT hosts file in hosts.skel file.
# If hosts.skel file exists, then NEW copy with customized unified hosts file will be copied to proper path.
# Next DNS Cache will be refreshed.
# YOU NEED RUNNING THIS SCRIPT FILE IN COMMAND LINE PROMPT WITH ADMINISTRATOR PRIVILIGES
#
# Might have to change change execute for the script file
# chmod 755 updaeHosts.sh
#
# ./updaeHosts.sh OR sh updaeHosts.sh

flushDNS() {
	# Find OS name
	#if Darwin (Mac OSX)
	#if Linux (Ubunut /Debian)

	OS=$(uname)
	echo $OS

	# Find Mac version and cleares the DNS Cache
	if [ "$OS" = "Darwin" ]
	then
		MAJOR_MAC_VERSION=$(sw_vers -productVersion | awk -F '.' '{print $2}')
		if [ "$MAJOR_MAC_VERSION" -ge "10" ]
		then
		 	sudo killall -HUP mDNSResponder
		else
			sudo dscacheutil -flushcache
		fi
	fi

	if [ "$OS" = "Linux" ]
	then
		# Find Unix version and cleares the DNS Cache
		MAJOR_UNIX_NAME=$(lsb_release -i | awk -F ":" '{print $2}')
		if [ "$MAJOR_UNIX_NAME" = "Ubuntu" ]
		then
			sudo /etc/rc.d/init.d/nscd restart
		fi
	fi

	echo "* * * DNS Cache Cleared * * *"
}

updateHosts() {
	echo "* * * Updating hosts * * *"
	python updateHostsFile.py -a >> /dev/null
	echo "* * * Copying hosts to /etc/hosts * * *"
	sudo cp hosts /etc/hosts
	flushDNS
}

if [ -f "/etc/hosts.skel" ]
then
	updateHosts
else
	echo "* * * Creating a Backup of current hosts file (/etc/hosts.skel) * * *"
	sudo cp /etc/hosts /etc/hosts.skel
	updateHosts
fi
