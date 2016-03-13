# Extensions

Use subfolders under the `extensions` folder to house extensions to the final unified hosts file.

Currently this repo includes three extensions: 

* `gambling` for common online betting sites,  
* `social` for common social media sites, and 
* `porn` for porn sites.  You can optionally add either or both to your final unified file.

Here are some sample calls, which vary which extensions are included.

**Using Python 3**:

    python3 updateHostsFile.py -auto --extensions porn social gambling

or, in short form:

    python3 updateHostsFile.py -a -e porn social gambling



**Using Python 2.7**:

    python updateHostsFile.py -auto --extensions porn social gambling

or, in short form:

    python updateHostsFile.py -a -e porn social gambling


More built-in extensions are coming soon.


---------------------------------------

Added extensions from https://github.com/pi-hole/pi-hole/blob/master/adlists.default:

 * http://adblock.gjtech.net/?format=unix-hosts
 * http://mirror1.malwaredomains.com/files/justdomains
 * http://sysctl.org/cameleon/hosts
 * https://zeustracker.abuse.ch/blocklist.php?download=domainblocklist
 * https://s3.amazonaws.com/lists.disconnect.me/simple_tracking.txt
 * https://s3.amazonaws.com/lists.disconnect.me/simple_ad.txt
 * hosts-file.net list. Updated frequently, but has been known to block legitimate sites. http://hosts-file.net/ad_servers.txt
 * Mahakala list. Has been known to block legitimage domains including the entire .com range: http://adblock.mahakala.is/
 * ADZHOSTS list. Has been known to block legitimate domains: http://optimate.dl.sourceforge.net/project/adzhosts/HOSTS.txt
 * Windows 10 telemetry list - warning this one may block windows update: https://raw.githubusercontent.com/crazy-max/HostsWindowsBlocker/master/hosts.txt
 * Securemecca.com list - Also blocks "adult" sites (pornography/gambling etc): http://securemecca.com/Downloads/hosts.txt (untested)
 * Quidsup's tracker list: https://raw.githubusercontent.com/quidsup/notrack/master/trackers.txt
 * Untested: https://raw.githubusercontent.com/reek/anti-adblock-killer/master/anti-adblock-killer-filters.txt
 * Untested: http://spam404bl.com/spam404scamlist.txt
 * Untested: http://malwaredomains.lehigh.edu/files/domains.txt