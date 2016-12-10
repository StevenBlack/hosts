#!/usr/bin/env python

# Script by Ben Limmer
# https://github.com/l1m5
#
# This Python script will combine all the host files you provide
# as sources into one, unique host file to keep you internet browsing happy.

# pylint: disable=invalid-name
# pylint: disable=bad-whitespace

# Making Python 2 compatible with Python 3
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import platform
import re
import shutil
import string
import subprocess
import sys
import tempfile
import time
import glob
import argparse
import socket
import json
import zipfile
import zlib

# zip files are not used actually, support deleted
# StringIO is not needed in Python 3
# Python 3 works differently with urlopen

try:                 # Python 3
    from urllib.parse import urlparse, urlencode
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
except ImportError:  # Python 2
    from urlparse import urlparse
    from urllib import urlencode
    from urllib2 import urlopen, Request, HTTPError

try:               # Python 2
    raw_input
except NameError:  # Python 3
    raw_input = input

# Detecting Python 3 for version-dependent implementations
Python3 = sys.version_info >= (3,0)

# This function handles both Python 2 and Python 3
def getFileByUrl(url):
    try:
        f = urlopen(url)
        return f.read().decode("UTF-8")
    except:
        print ("Problem getting file: ", url)
        # raise

# In Python 3   "print" is a function, braces are added everywhere

# Cross-python writing function
def writeData(f, data):
    if Python3:
        f.write(bytes(data, "UTF-8"))
    else:
        f.write(str(data).encode("UTF-8"))

# This function doesn't list hidden files
def listdir_nohidden(path):
    return glob.glob(os.path.join(path, "*"))

# Project Settings
BASEDIR_PATH = os.path.dirname(os.path.realpath(__file__))

defaults = {
    "numberofrules" : 0,
    "datapath" : os.path.join(BASEDIR_PATH, "data"),
    "freshen" : True,
    "replace" : False,
    "backup" : False,
    "skipstatichosts": False,
    "extensionspath" : os.path.join(BASEDIR_PATH, "extensions"),
    "extensions" : [],
    "outputsubfolder" : "",
    "datafilenames" : "hosts",
    "targetip" : "0.0.0.0",
    "ziphosts" : False,
    "sourcedatafilename" : "update.json",
    "readmefilename" : "readme.md",
    "readmetemplate" : os.path.join(BASEDIR_PATH, "readme_template.md"),
    "readmedata" : {},
    "readmedatafilename" : os.path.join(BASEDIR_PATH, "readmeData.json"),
    "exclusionpattern" : "([a-zA-Z\d-]+\.){0,}",
    "exclusionregexs" : [],
    "exclusions" : [],
    "commonexclusions" : ["hulu.com"],
    "whitelistfile" : os.path.join(BASEDIR_PATH, "whitelist")}

def main():

    parser = argparse.ArgumentParser(description="Creates a unified hosts file from hosts stored in data subfolders.")
    parser.add_argument("--auto", "-a", dest="auto", default=False, action="store_true", help="Run without prompting.")
    parser.add_argument("--backup", "-b", dest="backup", default=False, action="store_true", help="Backup the hosts files before they are overridden.")
    parser.add_argument("--extensions", "-e", dest="extensions", default=[], nargs="*", help="Host extensions to include in the final hosts file.")
    parser.add_argument("--ip", "-i", dest="targetip", default="0.0.0.0", help="Target IP address. Default is 0.0.0.0.")
    parser.add_argument("--zip", "-z", dest="ziphosts", default=False, action="store_true", help="Additionally create a zip archive of the hosts file.")
    parser.add_argument("--noupdate", "-n", dest="noupdate", default=False, action="store_true", help="Don't update from host data sources.")
    parser.add_argument("--skipstatichosts", "-s", dest="skipstatichosts", default=False, action="store_true", help="Skip static localhost entries in the final hosts file.")
    parser.add_argument("--output", "-o", dest="outputsubfolder", default="", help="Output subfolder for generated hosts file.")
    parser.add_argument("--replace", "-r", dest="replace", default=False, action="store_true", help="Replace your active hosts file with this new hosts file.")
    parser.add_argument("--flush-dns-cache", "-f", dest="flushdnscache", default=False, action="store_true", help="Attempt to flush DNS cache after replacing the hosts file.")

    global  settings

    options = vars(parser.parse_args())

    options["outputpath"] = os.path.join(BASEDIR_PATH, options["outputsubfolder"])
    options["freshen"] = not options["noupdate"]

    settings = {}
    settings.update(defaults)
    settings.update(options)

    settings["sources"] = listdir_nohidden(settings["datapath"])
    settings["extensionsources"] = listdir_nohidden(settings["extensionspath"])


    # All our extensions folders...
    settings["extensions"] = [os.path.basename(item) for item in listdir_nohidden(settings["extensionspath"])]
    # ... intersected with the extensions passed-in as arguments, then sorted.
    settings["extensions"]  = sorted( list(set(options["extensions"]).intersection(settings["extensions"])) )

    with open(settings["readmedatafilename"], "r") as f:
        settings["readmedata"] = json.load(f)

    promptForUpdate()
    promptForExclusions()
    mergeFile = createInitialFile()
    removeOldHostsFile()
    finalFile = removeDupsAndExcl(mergeFile)
    finalizeFile(finalFile)

    if settings["ziphosts"]:
        zf = zipfile.ZipFile(os.path.join(settings["outputsubfolder"], "hosts.zip"), mode='w')
        zf.write(os.path.join(settings["outputsubfolder"], "hosts"), compress_type=zipfile.ZIP_DEFLATED, arcname='hosts')
        zf.close()

    updateReadmeData()
    printSuccess("Success! The hosts file has been saved in folder " + settings["outputsubfolder"] + "\nIt contains " +
                 "{:,}".format(settings["numberofrules"]) + " unique entries.")

    promptForMove(finalFile)

# Prompt the User
def promptForUpdate():
    # Create hosts file if it doesn't exists
    if not os.path.isfile(os.path.join(BASEDIR_PATH, "hosts")):
        try:
            open(os.path.join(BASEDIR_PATH, "hosts"), "w+").close()
        except:
            printFailure("ERROR: No 'hosts' file in the folder, try creating one manually")

    if not settings["freshen"]:
        return

    response = "yes" if settings["auto"] else query_yes_no("Do you want to update all data sources?")
    if response == "yes":
        updateAllSources()
    else:
        if not settings["auto"]:
            print ("OK, we'll stick with what we've  got locally.")

def promptForExclusions():
    response = "no" if settings["auto"] else query_yes_no("Do you want to exclude any domains?\n" +
                            "For example, hulu.com video streaming must be able to access " +
                            "its tracking and ad servers in order to play video.")
    if response == "yes":
        displayExclusionOptions()
    else:
        if not settings["auto"]:
            print ("OK, we'll only exclude domains in the whitelist.")

def promptForMoreCustomExclusions(question="Do you have more domains you want to enter?"):
    return query_yes_no(question) == "yes"


def promptForFlushDnsCache():
    if settings['auto']:
        if settings['flushdnscache']:
            flushDnsCache()
    else:
        if settings['flushdnscache'] or query_yes_no("Attempt to flush the DNS cache?"):
            flushDnsCache()


def promptForMove(finalFile):

    if settings["replace"] and not settings["skipstatichosts"]:
        response = "yes"
    else:
        response = "no" if settings["auto"] or settings["skipstatichosts"] else query_yes_no("Do you want to replace your existing hosts file " +
                            "with the newly generated file?")
    if response == "yes":
        moveHostsFileIntoPlace(finalFile)
        promptForFlushDnsCache()
    else:
        return False
# End Prompt the User

# Exclusion logic
def displayExclusionOptions():
    for exclusionOption in settings["commonexclusions"]:
        response = query_yes_no("Do you want to exclude the domain " + exclusionOption + " ?")
        if response == "yes":
            excludeDomain(exclusionOption)
        else:
            continue
    response = query_yes_no("Do you want to exclude any other domains?")
    if response == "yes":
        gatherCustomExclusions()

def gatherCustomExclusions():
    while True:
        # Cross-python Input
        domainFromUser = raw_input("Enter the domain you want to exclude (e.g. facebook.com): ")
        if isValidDomainFormat(domainFromUser):
            excludeDomain(domainFromUser)
        if not promptForMoreCustomExclusions():
            return

def excludeDomain(domain):
    settings["exclusionregexs"].append(re.compile(settings["exclusionpattern"] + domain))

def matchesExclusions(strippedRule):
    strippedDomain = strippedRule.split()[1]
    for exclusionRegex in settings["exclusionregexs"]:
        if exclusionRegex.search(strippedDomain):
            return True
    return False
# End Exclusion Logic

# Update Logic
def updateAllSources():
    allsources = list(set(settings["sources"]) | set(settings["extensionsources"]))
    for source in allsources:
        if os.path.isdir(source):
            for updateURL in getUpdateURLsFromFile(source):
                print ("Updating source " + os.path.basename(source) + " from " + updateURL)
                # Cross-python call
                updatedFile = getFileByUrl(updateURL)
                try:
                    updatedFile = updatedFile.replace("\r", "") #get rid of carriage-return symbols
                    # This is cross-python code
                    dataFile = open(os.path.join(settings["datapath"], source, settings["datafilenames"]), "wb")
                    writeData(dataFile, updatedFile)
                    dataFile.close()
                except:
                    print ("Skipping.")

def getUpdateURLsFromFile(source):
    pathToUpdateFile = os.path.join(settings["datapath"], source, settings["sourcedatafilename"])
    if os.path.exists(pathToUpdateFile):
        updateFile = open(pathToUpdateFile, "r")
        updateData = json.load(updateFile)
        retURLs    = [updateData["url"]]
        updateFile.close()
    else:
        retURLs = None
        printFailure("Warning: Can't find the update file for source " + source + "\n" +
                     "Make sure that there's a file at " + pathToUpdateFile)
    return retURLs
# End Update Logic


def getUpdateURLFromFile(source):
    pathToUpdateFile = os.path.join(settings["datapath"], source, settings["sourcedatafilename"])
    if os.path.exists(pathToUpdateFile):
        with open(pathToUpdateFile, "r") as updateFile:
            updateData = json.load(updateFile)
            return [updateData["url"]]
    printFailure("Warning: Can't find the update file for source " + source + "\n" +
                 "Make sure that there's a file at " + pathToUpdateFile)
    return None
# End Update Logic

# File Logic
def createInitialFile():
    mergeFile = tempfile.NamedTemporaryFile()
    for source in settings["sources"]:
        filename = os.path.join(settings["datapath"], source, settings["datafilenames"])
        with open(filename, "r") as curFile:
            #Done in a cross-python way
            writeData(mergeFile, curFile.read())

    for source in settings["extensions"]:
        filename = os.path.join(settings["extensionspath"], source, settings["datafilenames"])
        with open(filename, "r") as curFile:
            #Done in a cross-python way
            writeData(mergeFile, curFile.read())

    return mergeFile

def removeDupsAndExcl(mergeFile):
    numberOfRules = settings["numberofrules"]
    if os.path.isfile(settings["whitelistfile"]):
        with open(settings["whitelistfile"], "r") as ins:
            for line in ins:
                line = line.strip(" \t\n\r")
                if line and not line.startswith("#"):
                    settings["exclusions"].append(line)

    if not os.path.exists(settings["outputpath"]):
        os.makedirs(settings["outputpath"])

    # Another mode is required to read and write the file in Python 3
    finalFile = open(os.path.join(settings["outputpath"], "hosts"),
                     "w+b" if Python3 else "w+")

    mergeFile.seek(0) # reset file pointer
    hostnames = set(["localhost", "localhost.localdomain", "local", "broadcasthost"])
    exclusions = settings["exclusions"]
    for line in mergeFile.readlines():
        write = "true"
        # Explicit encoding
        line = line.decode("UTF-8")
        # replace tabs with space
        line = line.replace("\t+", " ")
        # Trim trailing whitespace
        line = line.rstrip() + "\n"
        # Testing the first character doesn't require startswith
        if line[0] == "#" or re.match(r'^\s*$', line[0]):
            # Cross-python write
            writeData(finalFile, line)
            continue
        if "::1" in line:
            continue

        strippedRule = stripRule(line) #strip comments
        if not strippedRule or matchesExclusions(strippedRule):
            continue
        hostname, normalizedRule = normalizeRule(strippedRule) # normalize rule
        for exclude in exclusions:
            if exclude in line:
                write = "false"
                break
        if normalizedRule and (hostname not in hostnames) and (write == "true"):
            writeData(finalFile, normalizedRule)
            hostnames.add(hostname)
            numberOfRules += 1

    settings["numberofrules"] = numberOfRules
    mergeFile.close()

    return finalFile

def normalizeRule(rule):
    result = re.search(r'^[ \t]*(\d+\.\d+\.\d+\.\d+)\s+([\w\.-]+)(.*)', rule)
    if result:
        hostname, suffix = result.group(2,3)
        hostname = hostname.lower().strip() # explicitly lowercase and trim the hostname
        if suffix:
            # add suffix as comment only, not as a separate host
            return hostname, "%s %s #%s\n" % (settings["targetip"], hostname, suffix)
        else:
            return hostname, "%s %s\n" % (settings["targetip"], hostname)
    print ("==>%s<==" % rule)
    return None, None

def finalizeFile(finalFile):
    writeOpeningHeader(finalFile)
    finalFile.close()

# Some sources put comments around their rules, for accuracy we need to strip them
# the comments are preserved in the output hosts file
def stripRule(line):
    splitLine = line.split()
    if len(splitLine) < 2 :
        # just return blank
        return ""
    else:
        return splitLine[0] + " " + splitLine[1]

def writeOpeningHeader(finalFile):
    finalFile.seek(0) #reset file pointer
    fileContents = finalFile.read()  #save content
    finalFile.seek(0) #write at the top
    writeData(finalFile, "# This hosts file is a merged collection of hosts from reputable sources,\n")
    writeData(finalFile, "# with a dash of crowd sourcing via Github\n#\n")
    writeData(finalFile, "# Date: " + time.strftime("%B %d %Y", time.gmtime()) + "\n")
    if settings["extensions"]:
        writeData(finalFile, "# Extensions added to this file: " + ", ".join(settings["extensions"]) + "\n")
    writeData(finalFile, "# Number of unique domains: " + "{:,}\n#\n".format(settings["numberofrules"]))
    writeData(finalFile, "# Fetch the latest version of this file: https://raw.githubusercontent.com/StevenBlack/hosts/master/"+ os.path.join(settings["outputsubfolder"],"") + "hosts\n")
    writeData(finalFile, "# Project home page: https://github.com/StevenBlack/hosts\n#\n")
    writeData(finalFile, "# ===============================================================\n")
    writeData(finalFile, "\n")

    if not settings["skipstatichosts"]:
        writeData(finalFile, "127.0.0.1 localhost\n")
        writeData(finalFile, "127.0.0.1 localhost.localdomain\n")
        writeData(finalFile, "127.0.0.1 local\n")
        writeData(finalFile, "255.255.255.255 broadcasthost\n")
        writeData(finalFile, "::1 localhost\n")
        writeData(finalFile, "fe80::1%lo0 localhost\n")
        if platform.system() == "Linux":
            writeData(finalFile, "127.0.1.1 " + socket.gethostname() + "\n")
        writeData(finalFile, "\n")

    preamble = os.path.join(BASEDIR_PATH, "myhosts")
    if os.path.isfile(preamble):
        with open(preamble, "r") as f:
            writeData(finalFile, f.read())

    finalFile.write(fileContents)

def updateReadmeData():
    extensionsKey = "base"
    hostsLocation = ""
    if settings["extensions"]:
        extensionsKey = "-".join(settings["extensions"])

    generationData = {"location": os.path.join(settings["outputsubfolder"], ""),
                      "entries": settings["numberofrules"]}
    settings["readmedata"][extensionsKey] = generationData
    with open(settings["readmedatafilename"], "w") as f:
        json.dump(settings["readmedata"], f)


def moveHostsFileIntoPlace(finalFile):
    if os.name == "posix":
        print ("Moving the file requires administrative privileges. " +
               "You might need to enter your password.")
        if subprocess.call(["/usr/bin/sudo", "cp", os.path.abspath(finalFile.name), "/etc/hosts"]):
            printFailure("Moving the file failed.")
    elif os.name == "nt":
        print("Automatically moving the hosts file in place is not yet supported.")
        print("Please move the generated file to %SystemRoot%\system32\drivers\etc\hosts")


def flushDnsCache():
    print("Flushing the DNS cache to utilize new hosts file...")
    print("Flushing the DNS cache requires administrative privileges. " +
          "You might need to enter your password.")
    dnsCacheFound = False
    if platform.system() == "Darwin":
        if subprocess.call(["/usr/bin/sudo", "killall", "-HUP", "mDNSResponder"]):
            printFailure("Flushing the DNS cache failed.")
    else:
        if os.path.isfile("/etc/rc.d/init.d/nscd"):
            dnsCacheFound = True
            if subprocess.call(["/usr/bin/sudo", "/etc/rc.d/init.d/nscd", "restart"]):
                printFailure("Flushing the DNS cache failed.")
            else:
                printSuccess("Flushing DNS by restarting nscd succeeded")
        if os.path.isfile("/usr/lib/systemd/system/NetworkManager.service"):
            dnsCacheFound = True
            if subprocess.call(["/usr/bin/sudo", "/usr/bin/systemctl", "restart", "NetworkManager.service"]):
                printFailure("Flushing the DNS cache failed.")
            else:
                printSuccess("Flushing DNS by restarting NetworkManager succeeded")
        if os.path.isfile("/usr/lib/systemd/system/wicd.service"):
            dnsCacheFound = True
            if subprocess.call(["/usr/bin/sudo", "/usr/bin/systemctl", "restart", "wicd.service"]):
                printFailure("Flushing the DNS cache failed.")
            else:
                printSuccess("Flushing DNS by restarting wicd succeeded")
        if os.path.isfile("/usr/lib/systemd/system/dnsmasq.service"):
            dnsCacheFound = True
            if subprocess.call(["/usr/bin/sudo", "/usr/bin/systemctl", "restart", "dnsmasq.service"]):
                printFailure("Flushing the DNS cache failed.")
            else:
                printSuccess("Flushing DNS by restarting dnsmasq succeeded")
        if os.path.isfile("/usr/lib/systemd/system/networking.service"):
            dnsCacheFound = True
            if subprocess.call(["/usr/bin/sudo", "/usr/bin/systemctl", "restart", "networking.service"]):
                printFailure("Flushing the DNS cache failed.")
            else:
                printSuccess("Flushing DNS by restarting networking.service succeeded")
        if not dnsCacheFound:
            printFailure("Unable to determine DNS management tool.")


def removeOldHostsFile():               # hotfix since merging with an already existing hosts file leads to artefacts and duplicates
    oldFilePath = os.path.join(BASEDIR_PATH, "hosts")
    open(oldFilePath, "a").close()        # create if already removed, so remove wont raise an error

    if settings["backup"]:
        backupFilePath = os.path.join(BASEDIR_PATH, "hosts-{}".format(time.strftime("%Y-%m-%d-%H-%M-%S")))
        shutil.copy(oldFilePath, backupFilePath) # make a backup copy, marking the date in which the list was updated

    os.remove(oldFilePath)
    open(oldFilePath, "a").close()        # create new empty hostsfile

# End File Logic

# Helper Functions
## {{{ http://code.activestate.com/recipes/577058/ (r2)
def query_yes_no(question, default = "yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes":"yes", "y":"yes", "ye":"yes",
             "no":"no", "n":"no"}
    prompt = {None: " [y/n] ",
              "yes": " [Y/n] ",
              "no": " [y/N] "}.get(default, None)
    if not prompt:
        raise ValueError("invalid default answer: '%s'" % default)

    while 1:
        sys.stdout.write(colorize(question, colors.PROMPT) + prompt)
        # Changed to be cross-python
        choice = raw_input().lower()
        if default and not choice:
            return default
        elif choice in valid:
            return valid[choice]
        else:
            printFailure(
                "Please respond with 'yes' or 'no' (or 'y' or 'n').\n")
## end of http://code.activestate.com/recipes/577058/ }}}

def isValidDomainFormat(domain):
    if domain == "":
        print ("You didn't enter a domain. Try again.")
        return False
    domainRegex = re.compile("www\d{0,3}[.]|https?")
    if domainRegex.match(domain):
        print ("The domain " + domain + " is not valid. " +
               "Do not include www.domain.com or http(s)://domain.com. Try again.")
        return False
    else:
        return True

# Colors
class colors:
    PROMPT  = "\033[94m"
    SUCCESS = "\033[92m"
    FAIL    = "\033[91m"
    ENDC    = "\033[0m"

def colorize(text, color):
    return color + text + colors.ENDC

def printSuccess(text):
    print (colorize(text, colors.SUCCESS))

def printFailure(text):
    print (colorize(text, colors.FAIL))
# End Helper Functions

if __name__ == "__main__":
    main()
