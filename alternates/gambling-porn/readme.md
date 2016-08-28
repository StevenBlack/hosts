#Unified hosts file with gambling, porn extensions

This repository consolidates several reputable `hosts` files, and merges them into a unified hosts file
with duplicates removed.  This repo provides several hosts files tailored to you need to block.

* Last updated: **August 28 2016**.
* Here's the [raw hosts file with gambling, porn extensions](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/gambling-porn/hosts) containing 32,391 entries.

### List of all hosts file variants

Host file recipe | Readme | Raw hosts | Unique domains
---------------- |:------:|:---------:|:-------------:
Unified hosts = **(adware + malware)** | [Readme](https://github.com/StevenBlack/hosts/blob/master/readme.md) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts) | 26,391
Unified hosts **+ gambling** | [Readme](https://github.com/StevenBlack/hosts/blob/master/alternates/gambling/readme.md) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/gambling/hosts) | 27,105
Unified hosts **+ porn** | [Readme](https://github.com/StevenBlack/hosts/blob/master/alternates/porn/readme.md) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/porn/hosts) | 31,677
Unified hosts **+ social** | [Readme](https://github.com/StevenBlack/hosts/blob/master/alternates/social/readme.md) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/social/hosts) | 26,621
Unified hosts **+ gambling + porn** | [Readme](https://github.com/StevenBlack/hosts/blob/master/alternates/gambling-porn/readme.md) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/gambling-porn/hosts) | 32,391
Unified hosts **+ gambling + social** | [Readme](https://github.com/StevenBlack/hosts/blob/master/alternates/gambling-social/readme.md) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/gambling-social/hosts) | 27,335
Unified hosts **+ porn + social** | [Readme](https://github.com/StevenBlack/hosts/blob/master/alternates/porn-social/readme.md) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/porn-social/hosts) | 31,907
Unified hosts **+ gambling + porn + social** | [Readme](https://github.com/StevenBlack/hosts/blob/master/alternates/gambling-porn-social/readme.md) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/gambling-porn-social/hosts) | 32,621


**Expectation**: These unified hosts files should serve all devices, regardless of OS.

## Sources of hosts data unified here

Updated `hosts` files from the following locations are always unified and included:

* The [Adaway hosts file](http://adaway.org/hosts.txt), updated regularly.
* MVPs.org Hosts file at [http://winhelp2002.mvps.org/hosts.htm](http://winhelp2002.mvps.org/hosts.htm), updated
monthly, or thereabouts.
* Dan Pollock at [http://someonewhocares.org/hosts/](http://someonewhocares.org/hosts/) updated regularly.
* Malware Domain List at [http://www.malwaredomainlist.com/](http://www.malwaredomainlist.com/), updated regularly.
* Peter Lowe at [http://pgl.yoyo.org/adservers/](http://pgl.yoyo.org/adservers/), updated regularly.
* My own small list in raw form [here](https://raw.github.com/StevenBlack/hosts/master/data/StevenBlack/hosts).

## Extensions
The unified hosts file is extensible.  You manage extensions by curating the `extensions/` folder tree.
See the `social`, `gambling`, and `porn` extension which are included in this repo, for example.

## Generate your own unified hosts file

The `updateHostsFile.py` script, which is python 2.7 and Python 3-compatible, will generate a unified hosts file
based on the sources in the local `data/` subfolder.  The script will prompt you Whether it should fetch updated
versions (from locations defined by the update.info text file in each source's folder), otherwise it will use the
`hosts` file that's already there.

### Usage

#### Using Python 3:

    python3 updateHostsFile.py [--auto] [--replace] [--ip nnn.nnn.nnn.nnn] [--extensions ext1 ext2 ext3]

#### Using Python 2.7:

    python updateHostsFile.py [--auto] [--replace] [--ip nnn.nnn.nnn.nnn] [--extensions ext1 ext2 ext3]

#### Command line options:

`--help`, or `-h`: display help.

`--auto`, or `-a`: run the script without prompting. When `--auto` is invoked,

* Hosts data sources, including extensions, are updated.
* No extensions are included by default.  Use the `--extensions` or `-e` flag to include any you want.
* Your active hosts file is *not* replaced unless you include the `--replace` flag.

`--backup`, or `-b`: Make a backup of existing hosts file(s) as you generate over them.

`--extensions <ext1> <ext2> <ext3>`, or `-e <ext1> <ext2> <ext3>`: the names of subfolders below the `extensions` folder
containing additional category-specific hosts files to include in the amalgamation. Example: `--extensions porn` or
`-e social porn`.

`--flush-dns-cache`, or `-f`: skip the prompt for flushing the DNS cache.  Only active when `--replace` is also active.

`--ip nnn.nnn.nnn.nnn`, or `-i nnn.nnn.nnn.nnn`: the IP address to use as the target.  Default is `0.0.0.0`.

`--noupdate`, or `-n`: skip fetching updates from hosts data sources.

`--output <subfolder>`, or `-o <subfolder>`: place the generated source file in a subfolder.  If the subfolder does not
exist, it will be created.

`--replace`, or `-r`: trigger replacing your active hosts

`--skipstatichosts`, or `-s`: `false` (default) or `true`, omit the standard section, at the top containing lines like `127.0.0.1 localhost`.  This is useful for configuring proximate DNS services on the local network.


## How do I control which sources are unified?

Add one or more  *additional* sources, each in a subfolder of the `data/` folder, and specify its update url in
`update.info` file.

Add one or more *optional* extensions, which originate from subfolders of the `extensions/` folder.  Again the url in
`update.info` controls where this extension finds its updates.

### How do I include my own custom domain mappings?

If you have custom hosts records, place them in file `myhosts`.  The contents of this file are prepended to the
unified hosts file during the update process.

The `myhosts` file is not tracked by git, so any changes you make won't be overridden when you `git pull` this repo from `origin` in the future.

### How do I prevent domains from being included?

The domains you list in the `whitelist` file are excluded from the final hosts file.  

The `whitelist` uses partial matching.  Therefore if you whitelist `google-analytics.com`, that domain and all its
subdomains won't be merged into the final hosts file.

The `whitelist` is not tracked by git, so any changes you make won't be overridden when you `git pull` this repo 
from `origin` in the future.


## What is a hosts file?

A hosts file, named `hosts` (with no file extension), is a plain-text file used by all operating
systems to map hostnames to IP addresses.

In most operating systems, the `hosts` file is preferential to `DNS`.  Therefore if a domain name is
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


## We recommend using `0.0.0.0` instead of `127.0.0.1`
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
```
sudo dscacheutil -flushcache;sudo killall -HUP mDNSResponder
```

### Windows

|Run `updateHostsWindows.bat` in Command Prompt in repository dir always after updating main hosts file for easy replacing hosts file in Windows and reload DNS cache.|
:---------------------------------------------------------------------------------------------------------------------------------------------------------------------|

|WARNING: Don't run this BAT file directly from popup menu. You have been warned.|
:---------------------------------------------------------------------------------

Open a Command Prompt in directory where are files from this repository:

**Windows XP**: Start -> Run -> `cmd`

**Windows Vista, 7**: Start Button -> type `cmd` -> right-click Command Prompt ->
"Run as Administrator"

**Windows 8**: Start -> Swipe Up -> All Apps -> Windows System -> right-click Command Prompt ->
"Run as Administrator"

and run command:
```
updateHostsWindows.bat
```

### Linux
Open a Terminal and run with root privileges:

**Debian/Ubuntu** `sudo /etc/rc.d/init.d/nscd restart`

**Linux with systemd**: `sudo systemctl restart network.service`

**Fedora Linux**: `sudo systemctl restart NetworkManager.service`

**Arch Linux/Manjaro with Network Manager**: `sudo systemctl restart NetworkManager.service`

**Arch Linux/Manjaro with Wicd**: `sudo systemctl restart wicd.service`

**Others**: Consult [this wikipedia article](https://en.wikipedia.org/wiki/Hosts_%28file%29#Location_in_the_file_system).


## Goals of this unified hosts file

The goals of this repo are to:

1. automatically combine high-quality lists of hosts,

2. provide easy extensions,

3. de-dupe the resultant combined list,

4. and keep the resultant file reasonably sized.

A high-quality source is defined here as one that is actively curated.  A hosts source should be frequently
updated by its maintainers with both additions and removals.  The larger the hosts file, the higher the level of
curation is expected.

For example, the (huge) hosts file from [hosts-file.net](http://hosts-file.net) is **not** included
here because it is very large (300,000+ entries) and doesn't currently display a corresponding high level of curation
activity.

It is expected that this unified hosts file will serve both desktop and mobile devices under a variety of operating
systems.
