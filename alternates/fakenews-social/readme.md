[![Build Status](https://travis-ci.org/StevenBlack/hosts.svg?branch=master)](https://travis-ci.org/StevenBlack/hosts)

### Cloning?  Use a shallow clone and avoid 400 Mb of history

A **shallow clone** is a good idea because you probably don't need many years of history.

Like this:

    git clone --depth 5 https://github.com/StevenBlack/hosts.git

To run unit tests, in the top level directory, just run:

    python testUpdateHostsFile.py

**Note** if you are using Python 2, you must first install the `mock` library:

    pip install mock

Afterwards, you can follow the instructions above.

# Unified hosts file with fakenews, social extensions

This repository consolidates several reputable `hosts` files, and merges them
into a unified hosts file with duplicates removed.  This repo provides several
hosts files tailored to you need to block.

* Last updated: **July 11 2017**.
* Here's the [raw hosts file with fakenews, social extensions](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/fakenews-social/hosts) containing 37,669 entries.


### List of all hosts file variants

The **Non GitHub mirror** is the link to use for some hosts file managers like
[Hostsman for Windows](http://www.abelhadigital.com/hostsman) that don't work
with Github download links.

Host file recipe | Readme | Raw hosts | hosts (.zip) | Unique domains | Non Github mirror
---------------- |:------:|:---------:|:------------:|:--------------:|:-------------:
Unified hosts = **(adware + malware)** | [Readme](https://github.com/StevenBlack/hosts/blob/master/readme.md) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts.zip) | 36,763 | [link](http://sbc.io/hosts/hosts)
Unified hosts **+ fakenews** | [Readme](https://github.com/StevenBlack/hosts/blob/master/alternates/fakenews/readme.md) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/fakenews/hosts) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/fakenews/hosts.zip) | 37,436 | [link](http://sbc.io/hosts/alternates/fakenews/hosts)
Unified hosts **+ gambling** | [Readme](https://github.com/StevenBlack/hosts/blob/master/alternates/gambling/readme.md) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/gambling/hosts) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/gambling/hosts.zip) | 38,281 | [link](http://sbc.io/hosts/alternates/gambling/hosts)
Unified hosts **+ porn** | [Readme](https://github.com/StevenBlack/hosts/blob/master/alternates/porn/readme.md) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/porn/hosts) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/porn/hosts.zip) | 44,620 | [link](http://sbc.io/hosts/alternates/porn/hosts)
Unified hosts **+ social** | [Readme](https://github.com/StevenBlack/hosts/blob/master/alternates/social/readme.md) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/social/hosts) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/social/hosts.zip) | 36,996 | [link](http://sbc.io/hosts/alternates/social/hosts)
Unified hosts **+ fakenews + gambling** | [Readme](https://github.com/StevenBlack/hosts/blob/master/alternates/fakenews-gambling/readme.md) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/fakenews-gambling/hosts) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/fakenews-gambling/hosts.zip) | 38,954 | [link](http://sbc.io/hosts/alternates/fakenews-gambling/hosts)
Unified hosts **+ fakenews + porn** | [Readme](https://github.com/StevenBlack/hosts/blob/master/alternates/fakenews-porn/readme.md) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/fakenews-porn/hosts) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/fakenews-porn/hosts.zip) | 45,293 | [link](http://sbc.io/hosts/alternates/fakenews-porn/hosts)
Unified hosts **+ fakenews + social** | [Readme](https://github.com/StevenBlack/hosts/blob/master/alternates/fakenews-social/readme.md) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/fakenews-social/hosts) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/fakenews-social/hosts.zip) | 37,669 | [link](http://sbc.io/hosts/alternates/fakenews-social/hosts)
Unified hosts **+ gambling + porn** | [Readme](https://github.com/StevenBlack/hosts/blob/master/alternates/gambling-porn/readme.md) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/gambling-porn/hosts) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/gambling-porn/hosts.zip) | 46,138 | [link](http://sbc.io/hosts/alternates/gambling-porn/hosts)
Unified hosts **+ gambling + social** | [Readme](https://github.com/StevenBlack/hosts/blob/master/alternates/gambling-social/readme.md) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/gambling-social/hosts) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/gambling-social/hosts.zip) | 38,514 | [link](http://sbc.io/hosts/alternates/gambling-social/hosts)
Unified hosts **+ porn + social** | [Readme](https://github.com/StevenBlack/hosts/blob/master/alternates/porn-social/readme.md) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/porn-social/hosts) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/porn-social/hosts.zip) | 44,853 | [link](http://sbc.io/hosts/alternates/porn-social/hosts)
Unified hosts **+ fakenews + gambling + porn** | [Readme](https://github.com/StevenBlack/hosts/blob/master/alternates/fakenews-gambling-porn/readme.md) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/fakenews-gambling-porn/hosts) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/fakenews-gambling-porn/hosts.zip) | 46,811 | [link](http://sbc.io/hosts/alternates/fakenews-gambling-porn/hosts)
Unified hosts **+ fakenews + gambling + social** | [Readme](https://github.com/StevenBlack/hosts/blob/master/alternates/fakenews-gambling-social/readme.md) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/fakenews-gambling-social/hosts) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/fakenews-gambling-social/hosts.zip) | 39,187 | [link](http://sbc.io/hosts/alternates/fakenews-gambling-social/hosts)
Unified hosts **+ fakenews + porn + social** | [Readme](https://github.com/StevenBlack/hosts/blob/master/alternates/fakenews-porn-social/readme.md) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/fakenews-porn-social/hosts) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/fakenews-porn-social/hosts.zip) | 45,526 | [link](http://sbc.io/hosts/alternates/fakenews-porn-social/hosts)
Unified hosts **+ gambling + porn + social** | [Readme](https://github.com/StevenBlack/hosts/blob/master/alternates/gambling-porn-social/readme.md) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/gambling-porn-social/hosts) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/gambling-porn-social/hosts.zip) | 46,371 | [link](http://sbc.io/hosts/alternates/gambling-porn-social/hosts)
Unified hosts **+ fakenews + gambling + porn + social** | [Readme](https://github.com/StevenBlack/hosts/blob/master/alternates/fakenews-gambling-porn-social/readme.md) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/fakenews-gambling-porn-social/hosts) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/fakenews-gambling-porn-social/hosts.zip) | 47,044 | [link](http://sbc.io/hosts/alternates/fakenews-gambling-porn-social/hosts)


**Expectation**: These unified hosts files should serve all devices, regardless 
of OS.

## Sources of hosts data unified in this variant

Updated `hosts` files from the following locations are always unified and 
included:

Host file source | Description | Home page | Raw hosts | Update frequency 
-----------------|-------------|:---------:|:---------:|:-------:
AdAway | AdAway is an open source ad blocker for Android using the hosts file. |[link](https://adaway.org/) | [raw](https://raw.githubusercontent.com/AdAway/adaway.github.io/master/hosts.txt) | occasionally 
add.2o7Net | 2o7Net tracking sites based on http://www.hostsfile.org/hosts.html content. |[link](https://github.com/FadeMind/hosts.extras) | [raw](https://raw.githubusercontent.com/FadeMind/hosts.extras/master/add.2o7Net/hosts) | occasionally 
add.Dead | Dead sites based on http://www.hostsfile.org/hosts.html content. |[link](https://github.com/FadeMind/hosts.extras) | [raw](https://raw.githubusercontent.com/FadeMind/hosts.extras/master/add.Dead/hosts) | occasionally 
add.Risk | Risk content sites based on http://www.hostsfile.org/hosts.html content. |[link](https://github.com/FadeMind/hosts.extras) | [raw](https://raw.githubusercontent.com/FadeMind/hosts.extras/master/add.Risk/hosts) | occasionally 
add.Spam | Spam sites based on http://www.hostsfile.org/hosts.html content. |[link](https://github.com/FadeMind/hosts.extras) | [raw](https://raw.githubusercontent.com/FadeMind/hosts.extras/master/add.Spam/hosts) | occasionally 
Mitchell Krog's - Badd Boyz Hosts | Sketchy domains and Bad Referrers from my Nginx and Apache Bad Bot and Spam Referrer Blockers |[link](https://github.com/mitchellkrogza/Badd-Boyz-Hosts) | [raw](https://raw.githubusercontent.com/mitchellkrogza/Badd-Boyz-Hosts/master/hosts) | weekly 
KADhosts | Fraud/adware/scam websites. |[link](https://github.com/azet12/KADhosts) | [raw](https://raw.githubusercontent.com/azet12/KADhosts/master/KADhosts.txt) | frequently 
Malware Domain List | Malware Domain List is a non-commercial community project. |[link](http://www.malwaredomainlist.com/) | [raw](https://www.malwaredomainlist.com/hostslist/hosts.txt) | weekly 
MVPS hosts file | The purpose of this site is to provide the user with a high quality custom HOSTS file. |[link](http://winhelp2002.mvps.org/) | [raw](http://winhelp2002.mvps.org/hosts.txt) | monthly 
Dan Pollock - someonewhocares.org | How to make the internet not suck (as much). |[link](http://someonewhocares.org/hosts/) | [raw](http://someonewhocares.org/hosts/zero/hosts) | frequently 
SpotifyAds | Spotify ads sources sites based on https://github.com/Xeroday/Spotify-Ad-Blocker content. |[link](https://github.com/FadeMind/hosts.extras) | [raw](https://raw.githubusercontent.com/FadeMind/hosts.extras/master/SpotifyAds/hosts) | occasionally 
Steven Black's ad-hoc list | Additional sketch domains as I come across them. |[link](https://github.com/StevenBlack/hosts/blob/master/data/StevenBlack/hosts) | [raw](https://raw.githubusercontent.com/StevenBlack/hosts/master/data/StevenBlack/hosts) | occasionally 
tyzbit | Microsoft tracking domains.  A fork of this repo providing additional data. |[link](https://github.com/tyzbit/hosts/blob/master/data/tyzbit/hosts) | [raw](https://raw.githubusercontent.com/tyzbit/hosts/master/data/tyzbit/hosts) | rarely 
UncheckyAds | Windows installers ads sources sites based on https://unchecky.com/ content. |[link](https://github.com/FadeMind/hosts.extras) | [raw](https://raw.githubusercontent.com/FadeMind/hosts.extras/master/UncheckyAds/hosts) | occasionally 
yoyo.org | Blocking with ad server and tracking server hostnames. |[link](https://pgl.yoyo.org/adservers/) | [raw](https://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts&mimetype=plaintext&useip=0.0.0.0) | frequently 
Fake News | An in-progress collection of fake news outlets. |[link](https://github.com/marktron/fakenews) | [raw](https://raw.githubusercontent.com/marktron/fakenews/master/fakenews) | occasional 
Sinfonietta's social media blocking hosts file | A collection of category-specific host files. |[link](https://github.com/Sinfonietta/hostfiles) | [raw](https://raw.githubusercontent.com/Sinfonietta/hostfiles/master/social-hosts) | occasional 



## Extensions
The unified hosts file is extensible.  You manage extensions by curating the 
`extensions/` folder tree. See the `social`, `gambling`, and `porn` extension 
folders.

## Generate your own unified hosts file

The `updateHostsFile.py` script, which is python 2.7 and Python 3-compatible,
will generate a unified hosts file based on the sources in the local `data/`
subfolder.  The script will prompt you Whether it should fetch updated
versions (from locations defined by the `update.json` text file in each
source's folder), otherwise it will use the `hosts` file that's already there.

### Usage

#### Using Python 3:

    python3 updateHostsFile.py [--auto] [--replace] [--ip nnn.nnn.nnn.nnn] [--extensions ext1 ext2 ext3]

#### Using Python 2.7:

    python updateHostsFile.py [--auto] [--replace] [--ip nnn.nnn.nnn.nnn] [--extensions ext1 ext2 ext3]

#### Command line options:

`--help`, or `-h`: display help.

`--auto`, or `-a`: run the script without prompting. When `--auto` is invoked,

* Hosts data sources, including extensions, are updated.
* No extensions are included by default.  Use the `--extensions` or `-e` flag 
to include any you want.
* Your active hosts file is *not* replaced unless you include the `--replace` 
flag.

`--backup`, or `-b`: Make a backup of existing hosts file(s) as you generate 
over them.

`--extensions <ext1> <ext2> <ext3>`, or `-e <ext1> <ext2> <ext3>`: the names 
of subfolders below the `extensions` folder containing additional 
category-specific hosts files to include in the amalgamation. Example: 
`--extensions porn` or `-e social porn`.

`--flush-dns-cache`, or `-f`: skip the prompt for flushing the DNS cache.  
Only active when `--replace` is also active.

`--ip nnn.nnn.nnn.nnn`, or `-i nnn.nnn.nnn.nnn`: the IP address to use as the 
target.  Default is `0.0.0.0`.

`--keepdomaincomments`, or `-k`: `false` (default) or `true`, keep the comments 
that appear on the same line as domains.  The default is `false` since some
router-based implementations can't handle comments in-line with hosts.

`--skipstatichosts`, or `-s`: `false` (default) or `true`, 

`--noupdate`, or `-n`: skip fetching updates from hosts data sources.

`--output <subfolder>`, or `-o <subfolder>`: place the generated source file 
in a subfolder.  If the subfolder does not exist, it will be created.

`--replace`, or `-r`: trigger replacing your active hosts

`--skipstatichosts`, or `-s`: `false` (default) or `true`, omit the standard
section at the top, containing lines like `127.0.0.1 localhost`.  This is
useful for configuring proximate DNS services on the local network.

`--zip`, or `-z`: `false` (default) or `true`, additionally create a zip
archive of the hosts file named `hosts.zip`.

## How do I control which sources are unified?

Add one or more  *additional* sources, each in a subfolder of the `data/`
folder, and specify the `url` key in its `update.json` file.

Add one or more *optional* extensions, which originate from subfolders of the
`extensions/` folder.  Again the url in `update.json` controls where this
extension finds its updates.

Create an *optional* `blacklist` file. The contents of this file (containing a
listing of additional domains in `hosts` file format) are appended to the
unified hosts file during the update process. A sample `blacklist` is
included, and may be modified as you desire.

  * NOTE: The `blacklist` is not tracked by git, so any changes you make won't
be overridden when you `git pull`   this repo from `origin` in the future.

### How do I include my own custom domain mappings?

If you have custom hosts records, place them in file `myhosts`.  The contents
of this file are prepended to the unified hosts file during the update
process.

The `myhosts` file is not tracked by git, so any changes you make won't be
overridden when you `git pull` this repo from `origin` in the future.

### How do I prevent domains from being included?

The domains you list in the `whitelist` file are excluded from the final hosts
file.

The `whitelist` uses partial matching.  Therefore if you whitelist
`google-analytics.com`, that domain and all its subdomains won't be merged
into the final hosts file.

The `whitelist` is not tracked by git, so any changes you make won't be
overridden when you `git pull` this repo  from `origin` in the future.


## What is a hosts file?

A hosts file, named `hosts` (with no file extension), is a plain-text file
used by all operating systems to map hostnames to IP addresses.

In most operating systems, the `hosts` file is preferential to `DNS`.
Therefore if a domain name is resolved by the `hosts` file, the request never
leaves your computer.

Having a smart `hosts` file goes a long way towards blocking malware, adware,
and other irritants.

For example, to nullify requests to some doubleclick.net servers, adding these
lines to your hosts file will do it:

    # block doubleClick's servers
    0.0.0.0 ad.ae.doubleclick.net
    0.0.0.0 ad.ar.doubleclick.net
    0.0.0.0 ad.at.doubleclick.net
    0.0.0.0 ad.au.doubleclick.net
    0.0.0.0 ad.be.doubleclick.net
    # etc...


## We recommend using `0.0.0.0` instead of `127.0.0.1`

Traditionally most host files use `127.0.0.1`, the *loopback address*, to establish an IP connection to the local machine.

We prefer to use `0.0.0.0`, which is defined as a non-routable meta-address used to designate an invalid, unknown,
or non applicable target.

Using `0.0.0.0` is empirically faster, possibly because there's no wait for a timeout resolution. It also does not
interfere with a web server that may be running on the local PC.

## Why not use just `0` instead of `0.0.0.0`?
We tried that.  Using `0` doesn't work universally.


## Location of your hosts file
To modify your current `hosts` file, look for it in the following places and modify it with a text
editor.

**Mac OS X, iOS, Android, Linux**: `/etc/hosts` folder.

**Windows**: `%SystemRoot%\system32\drivers\etc\hosts` folder.

## Updating hosts file on Windows

On Linux and Mac OS X, you can simply run the Python script, but on Windows, more
work is required due to compatibility issues in implementing some of the functionality
for Windows. It is preferable to run the batch file as follows:

```
updateHostsWindows.bat
```

This file MUST be run in command prompt with administrator privileges in
the repository directory. In addition to updating the hosts file, it can also
replace the existing hosts file, and reload the DNS cache. It goes without
saying that in order for this to work, you must be connected to the internet.

To open a command prompt as administrator in the repository's directory, do the following:

**Windows XP**: Start -> Run -> `cmd`

**Windows Vista, 7**: Start Button -> type `cmd` -> right-click Command Prompt ->
"Run as Administrator"

**Windows 8**: Start -> Swipe Up -> All Apps -> Windows System -> right-click Command Prompt ->
"Run as Administrator"

**Windows 10**: Start Button -> type `cmd` -> right-click Command Prompt ->
"Run as Administrator"

## Reloading hosts file
Your operating system will cache DNS lookups. You can either reboot or run the following commands to
manually flush your DNS cache once the new hosts file is in place.

### Windows

Open a command prompt with administrator privileges and run this command:

```
ipconfig /flushdns
```

|If you want to use a huge hosts file by merging [hphosts](https://www.hosts-file.net) (NOT INCLUDED HERE) you need to DISABLE and STOP `Dnscache` service before you replace hosts file in Windows Systems. You have been warned.|
:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Before flushing the DNS cache, open a command prompt with administrator privileges and run this command:

```
sc config "Dnscache" start= disabled
sc stop "Dnscache"
```

### Linux

Open a Terminal and run with root privileges:

**Debian/Ubuntu** `sudo /etc/rc.d/init.d/nscd restart`

**Linux with systemd**: `sudo systemctl restart network.service`

**Fedora Linux**: `sudo systemctl restart NetworkManager.service`

**Arch Linux/Manjaro with Network Manager**: `sudo systemctl restart NetworkManager.service`

**Arch Linux/Manjaro with Wicd**: `sudo systemctl restart wicd.service`

**Others**: Consult [this wikipedia article](https://en.wikipedia.org/wiki/Hosts_%28file%29#Location_in_the_file_system).

### Mac OS X

Open a Terminal and run:
```
sudo dscacheutil -flushcache;sudo killall -HUP mDNSResponder
```

## Goals of this unified hosts file

The goals of this repo are to:

1. automatically combine high-quality lists of hosts,

2. provide easy extensions,

3. de-dupe the resultant combined list,

4. and keep the resultant file reasonably sized.

A high-quality source is defined here as one that is actively curated.  A
hosts source should be frequently updated by its maintainers with both
additions and removals.  The larger the hosts file, the higher the level of
curation is expected.

For example, the (huge) hosts file from [hosts-file.net](http://hosts-file.net)
is **not** included here because it is very large (300,000+ entries)
and doesn't currently display a corresponding high level of curation activity.

It is expected that this unified hosts file will serve both desktop and mobile
devices under a variety of operating systems.

## Interesting Applications

* [Block ads and malware via local DNS server](https://github.com/mueller-ma/block-ads-via-dns "Block ads and malware via local DNS server") (for Debian, Raspbian & Ubuntu): Set up a local DNS server with a `/etc/bind/named.conf.blocked` file, sourced from here.

* [Blocking ads and malwares with unbound](https://deadc0de.re/articles/unbound-blocking-ads.html "Blocking ads and malwares with unbound") - [Unbound](https://www.unbound.net/ "Unbound is a validating, recursive, and caching DNS resolver.")  is a validating, recursive, and caching DNS resolver.
