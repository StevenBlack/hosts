#Amalgamated hosts file

This repo consolidates several reputable `hosts` files and merges them into a single
amalgamated hosts file with duplicates removed.

**Currently this amalgamated hosts file contains 27,139 unique entries.**

## Goals of this amalgamated hosts file

The goals of this repo are to

1) automatically combine high-quality lists of hosts,

2) de-dupe the resultant combined list,

3) and keep the resultant file reasonably sized.

A high-quality source is defined here as one that is actively curated.  A hosts source should be frequently
updated by its maintainers with both additions and removals.  The larger the hosts file, the higher the level of
curation is expected.

For example, the (huge) hosts file from [hosts-file.net](http://hosts-file.net) is **not** included
here because it is very large (300,000+ entries) and doesn't currently display a corresponding high level of curation
activity.

It is expected that this amalgamated hosts file will serve both desktop and mobile devices under a variety of operating
systems.

## Sources of host data amalgamated here

Currently the `hosts` files from the following locations are amalgamated:

* The [Adaway hosts file](http://adaway.org/hosts.txt), updated regularly.
* MVPs.org Hosts file at [http://winhelp2002.mvps.org/hosts.htm](http://winhelp2002.mvps.org/hosts.htm), updated
monthly, or thereabouts.
* Dan Pollock at [http://someonewhocares.org/hosts/](http://someonewhocares.org/hosts/) updated regularly.
* Malware Domain List at [http://www.malwaredomainlist.com/](http://www.malwaredomainlist.com/), updated regularly.
* Peter Lowe at [http://pgl.yoyo.org/adservers/](http://pgl.yoyo.org/adservers/), updated regularly.
* My own small list in raw form [here](https://raw.github.com/StevenBlack/hosts/master/data/StevenBlack/hosts).

You can add additional sources by placing them in the `data/` directory. Provide a copy of that new
`hosts` file, and place its update url in `update.info`. The `updateHostsFile.py` routine will
automatically refresh the `hosts` file from source each time a new amalgamated file is generated.

## How do I incorporate my own hosts?

If you have custom host records, place them in file `myhosts`.  The contents of this file are prepended to the
amalgamated hosts file during the update process.

## Using updateHostsFile.py

This Python script will generate a unique hosts file based on the sources in the `data/` folder.
You can either have the script go out and fetch an updated version over the web (defined by the
update.info text file in the source's directory), or it will use the `hosts` file that's already
there.

Usage

    python updateHostsFile.py

**TAKE NOTE** this script is tested with Python version 2.7.10.

## What is a hosts file?

A hosts file, named `hosts` (with no file extension), is a plain-text file used by all operating
systems to map hostnames to IP addresses.

In most operating systems, the `hosts` file is preferential to `DNS`.  Therefore if a host name is
resolved by the `hosts` file, the request never leaves your computer.

Having a smart `hosts` file goes a long way towards blocking malware, adware, and other irritants.

For example, to nullify requests to some doubleclick.net servers, adding these lines to your hosts
file will do it:

    # block doubleClick's servers
    127.0.0.1 ad.ae.doubleclick.net
    127.0.0.1 ad.ar.doubleclick.net
    127.0.0.1 ad.at.doubleclick.net
    127.0.0.1 ad.au.doubleclick.net
    127.0.0.1 ad.be.doubleclick.net
    # etc...


## Why use `0.0.0.0` instead of `127.0.0.1`?
Using `0.0.0.0` is faster because you don't have to wait for a timeout. It also does not interfere
with a web server that may be running on the local PC.

## Why not use just `0` instead of `0.0.0.0`?
We tried that.  Using `0` doesn't work universally.


## Location of your hosts file
To modify your current `hosts` file, look for it in the following places and modify it with a text
editor.

**Mac OS X, iOS, Android, Linux**: `/etc/hosts` folder.

**Windows**: `%SystemRoot%\system32\drivers\etc\hosts` folder.

## Reloading hosts file
Your operating system will cache DNS lookups. You can either reboot or run the following commands to
manually flush your DNS cache once the new hosts file is in place.

### Mac OS X
Open a Terminal and run:

`sudo dscacheutil -flushcache;sudo killall -HUP mDNSResponder`

### Windows
Open a Command Prompt:

**Windows XP**: Start -> Run -> `cmd`

**Windows Vista, 7**: Start Button -> type `cmd` -> right-click Command Prompt ->
"Run as Administrator"

**Windows 8**: Start -> Swipe Up -> All Apps -> Windows System -> right-click Command Prompt ->
"Run as Administrator"

and run:

`ipconfig /flushdns`

### Linux
Open a Terminal and run with root privileges:

**Debian/Ubuntu** `sudo /etc/rc.d/init.d/nscd restart`

**Linux with systemd**: `sudo systemctl restart network.service`

**Fedora Linux**: `sudo systemctl restart NetworkManager.service`

**Arch Linux/Manjaro**: `sudo systemctl restart NetworkManager.service`
