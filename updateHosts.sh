#!/bin/bash

flushDNS() {
	# Find OS name
	#if Darwin (Mac OSX)
	#if Linux (Ubunut /Debian)

	OS=$(uname)

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

defaultHosts()
{
cat <<EOF

# IPv4

127.0.0.1 localhost
127.0.0.1 localhost.localdomain
127.0.0.1 local
255.255.255.255 broadcasthost

# IPv6

::1 localhost
fe80::1%lo0 localhost

EOF
}

# Restore default Hosts file.
restore()
{
  OUT=$(defaultHosts)
  echo "* * * Restoring default hosts * * *"
  echo "This is restored default hosts file: $OUT" > hosts
	sudo cp hosts /etc/hosts
  flushDNS
}

# Update Hosts file from various sources.
update() {
if [ -f "/etc/hosts.skel" ]
then
	updateHosts
else
	echo "* * * Creating a Backup of current hosts file (/etc/hosts.skel) * * *"
	sudo cp /etc/hosts /etc/hosts.skel
	updateHosts
fi
}

if [ "$1" = "-u" ] || [ "$1" = "--update" ]
then
  update
elif [ "$1" = "-r" ] || [ "$1" = "--restore" ]
then
  restore
else
  echo "Use this Script to update OR restore hosts file"
  echo ""
  echo "# Useage #"
  echo "./t.sh -u OR ./t.sh -r"
  echo ""
  echo "-u or --update  : to update the hosts file for various sources"
  echo "-r or --restore : to restore the hosts file to system default"
  echo ""
fi
