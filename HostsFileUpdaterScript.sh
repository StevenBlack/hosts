#!/bin/bash
# Hosts file updater
# You will probably need root or su rights to access /etc/hosts
# modified by Valkiry to be used withb Steven Black's Unified Hosts files.
#
# Debian users will need the package "sysutils" as this script uses dos2unix
# $ apt-get install sysutils
#
HFSERVER="https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts"
HFILE="hosts.txt"
ORIGFILE="/etc/hosts.original"

clear
echo "-------------------------------------------------------------"
echo "This script will update your Hosts file to the latest version of StevenBlack's Unified hosts = (adware + malware)"
echo "Your original Hosts file will be renamed to $ORIGFILE"
echo "-------------------------------------------------------------"
echo ""

if [ ! -f "$ORIGFILE" ] ; then
  echo "Backing up your previous hosts file.." 
  cp -v /etc/hosts $ORIGFILE # I like verbose file operations.  Can be less verbose if necessary.
fi

echo "Retrieving $HFILE from $HFSERVER"
echo ""
wget -O /tmp/$HFILE $HFSERVER/$HFILE
# Uncomment the line below to allow .zip file extraction of hosts files.  
#unzip -p /tmp/$HFILE | dos2unix > /tmp/hosts
if [ 'grep -c "banner" /tmp/hosts' ];then 
    echo "Downloaded and unpacked $HFILE OK"
    echo "Appending host list to original content"  # which was probably there for a reason, like to make sure localhost worked, and possibly even more stuff if part of a corporate LAN
    #cp -f -u /tmp/hosts /etc/hosts
    cat $ORIGFILE  >/etc/hosts
    echo "" >>/etc/hosts # to make sure the original file ends in a new-line so that 2 entries don't end up on the same line, either causing unexpected behavior or not working at all
    cat /tmp/hosts >>/etc/hosts
    rm -fv /tmp/hosts* # again, I like verbose file operations.  I like to know what my system is doing.
    echo "Update process complete"
    #echo "-------------------------------------------------------------"
    echo "As a side-effect of this script, any changes you wish to make"
    echo "persistent in the hosts file should be made to $ORIGFILE"
    echo "because /etc/hosts will be respawned from that file and the "
    echo "newlist from the server each time this script runs."
    exit
else
    echo "Update failed"
fi
