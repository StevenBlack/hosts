#Amalgamated hosts file

This repo consolidates several reputable `hosts` files and consolidates them into a single hosts file that you can use.

**Currently this hosts file contains 26823 unique entries.**

## Source of host data amalgamated here

Currently the `hosts` files from the following locations are amalgamated:

* The [Adaway hosts file](http://adaway.org/hosts.txt), updated regularly.
* MVPs.org Hosts file at [http://winhelp2002.mvps.org/hosts.htm](http://winhelp2002.mvps.org/hosts.htm), updated monthly, or thereabouts.
* Dan Pollock at [http://someonewhocares.org/hosts/](http://someonewhocares.org/hosts/) updated regularly.
* Malware Domain List at [http://www.malwaredomainlist.com/](http://www.malwaredomainlist.com/), updated regularly.
* Peter Lowe at [http://pgl.yoyo.org/adservers/](http://pgl.yoyo.org/adservers/), updated regularly.
* My own small list in raw form [here](https://raw.github.com/StevenBlack/hosts/master/data/StevenBlack/hosts).

You can add any additional sources you'd like under the data/ directory. Provide a copy of the current `hosts` file and a file called
update.info with the URL to the `hosts` file source. This will allow updateHostsFile.py to automatically update your source.

## Using updateHostsFile.py

This Python script will generate a unique hosts file based on the sources provided. You can either have the script go out and fetch an updated version over the web (defined by the update.info text file in the source's directory), or it will use the `hosts` file you already have checked into your source's data folder.

Usage

    python updateHostsFile.py
  
**TAKE NOTE** this script is tested with Python version 2.7.10.  I hope to have a Python 3 version soon.

## What is a hosts file?

A hosts file, named `hosts` (with no file extension), is a plain-text file used by all operating systems to map hostnames to IP addresses. 

In most operating systems, the `hosts` file is preferential to `DNS`.  Therefore if a host name is resolved by the `hosts` file, the request never leaves your computer.

Having a smart `hosts` file goes a long way towards blocking malware, adware, and other irritants.

For example, to nullify requests to some doubleclick.net servers, adding these lines to your hosts file will do it:

    # block doubleClick's servers
    127.0.0.1 ad.ae.doubleclick.net
    127.0.0.1 ad.ar.doubleclick.net
    127.0.0.1 ad.at.doubleclick.net
    127.0.0.1 ad.au.doubleclick.net
    127.0.0.1 ad.be.doubleclick.net
    # etc...


## Why use `0.0.0.0` instead of `127.0.0.1`?
Using `0.0.0.0` is faster.

## Why not use just `0` instead of `0.0.0.0`?
We tried that.  Using `0` doesn't work universally.


## Location of your hosts file
To modify your current `hosts` file, look for it in the following places and modify it with a text editor.

**Mac OS X, iOS, Android, Linux**: `/etc/hosts` folder.

**Windows**: `%SystemRoot%\system32\drivers\etc\hosts` folder.

## Reloading hosts file
Your operating system will cache DNS lookups. You can either reboot or run the following commands to manually flush your DNS cache once the new hosts file is in place.

### Mac OS X
Open a Terminal and run:

`dscacheutil -flushcache`

### Windows
Open a Command Prompt:

**Windows XP**: Start -> Run -> `cmd`

**Windows Vista, 7**: Start Button -> type `cmd` -> right-click Command Prompt -> "Run as Administrator"

**Windows 8**: Start -> Swipe Up -> All Apps -> Windows System -> right-click Command Prompt -> "Run as Administrator"

and run:

`ipconfig /flushdns`

### Linux
Open a Terminal and run:

`/etc/rc.d/init.d/nscd restart`

**Linux with systemd**: systemctl restart network.service

**Fedora Linux**: systemctl restart NetworkManager.service
