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
# zip files are not used actually, support deleted
# StringIO is not needed in Python 3
# Python 3 works differently with urlopen

# Supporting urlopen in Python 2 and Python 3
try:
    from urllib.parse import urlparse, urlencode
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
except ImportError:
    from urlparse import urlparse
    from urllib import urlencode
    from urllib2 import urlopen, Request, HTTPError

# This function handles both Python 2 and Python 3
def getFileByUrl(url):
    try:
        f = urlopen(url)
        return f.read().decode("UTF-8")
    except:
        print ("Problem getting file: ", url)
        # raise

# In Python 3   "print" is a function, braces are added everywhere

# Detecting Python 3 for version-dependent implementations
Python3     = False
cur_version = sys.version_info
if cur_version >= (3, 0):
    Python3 = True

# This function works in both Python 2 and Python 3
def myInput(msg = ""):
    if Python3:
        return input(msg)
    else:
        return raw_input(msg)

# Cross-python writing function
def writeData(f, data):
    if Python3:
        f.write(bytes(data, 'UTF-8'))
    else:
        f.write(str(data).encode('UTF-8'))

# This function doesn't list hidden files
def listdir_nohidden(path):
    return glob.glob(os.path.join(path, '*'))

# Project Settings
BASEDIR_PATH        = os.path.dirname(os.path.realpath(__file__))
DATA_PATH           = os.path.join(BASEDIR_PATH, 'data')
EXTENSIONS_PATH     = os.path.join(BASEDIR_PATH, 'extensions')
DATA_FILENAMES      = 'hosts'
UPDATE_URL_FILENAME = 'update.info'
SOURCES             = listdir_nohidden(DATA_PATH)
EXTENSIONS          = listdir_nohidden(EXTENSIONS_PATH)
README_TEMPLATE     = os.path.join(BASEDIR_PATH, 'readme_template.md')
README_FILENAME     = 'readme.md'
WHITELIST_FILE      = os.path.join(BASEDIR_PATH, 'whitelist')

# Exclusions
EXCLUSION_PATTERN = '([a-zA-Z\d-]+\.){0,}' #append domain the end
EXCLUSIONS        = []
# Common domains to exclude
COMMON_EXCLUSIONS = ['hulu.com']

# Global vars
outputPath = BASEDIR_PATH
exclusionRegexs = []
numberOfRules = 0
auto = False
update = True
replace = False
targetIP = "0.0.0.0"
extensions = []

def main():

    parser = argparse.ArgumentParser(description="Creates a unified hosts file from hosts stored in data subfolders.")
    parser.add_argument("--auto", "-a", dest="auto", default=False, action='store_true', help="Run without prompting.")
    parser.add_argument("--replace", "-r", dest="replace", default=False, action='store_true', help="Replace your active hosts file with this new hosts file.")
    parser.add_argument("--ip", "-i", dest="targetIP", default="0.0.0.0", help="Target IP address. Default is 0.0.0.0.")
    parser.add_argument("--extensions", "-e", dest="extensions", default=[], nargs='*', help="Host extensions to include in the final hosts file.")
    parser.add_argument("--output", "-o", dest="outputSubFolder", default="", help="Output subfolder for generated hosts file.")
    parser.add_argument("--noupdate", "-n", dest="noUpdate", default=False, action='store_true', help="Don't update from host data sources.")


    args = parser.parse_args()

    global auto, update, replace, targetIP, replace, extensions, outputPath
    auto = args.auto
    replace = args.replace
    targetIP = args.targetIP
    outputPath = os.path.join(BASEDIR_PATH, args.outputSubFolder)
    update = not args.noUpdate

    # All our extensions folders...
    extensions = [os.path.basename(item) for item in listdir_nohidden(EXTENSIONS_PATH)]
    # ... intersected with the extensions passed-in as arguments, then sorted.
    extensions = sorted( list(set(args.extensions).intersection(extensions)) )

    promptForUpdate()
    promptForExclusions()
    mergeFile = createInitialFile()
    removeOldHostsFile()
    finalFile = removeDupsAndExcl(mergeFile)
    finalizeFile(finalFile)
    updateReadme(numberOfRules)
    printSuccess('Success! The hosts file has been saved in folder\n' + outputPath + '\nIt contains ' +
                 "{:,}".format(numberOfRules) + ' unique entries.')

    promptForMove(finalFile)

# Prompt the User
def promptForUpdate():
    # Create hosts file if it doesn't exists
    if not os.path.isfile(os.path.join(BASEDIR_PATH, 'hosts')):
        try:
            open(os.path.join(BASEDIR_PATH, 'hosts'), 'w+').close()
        except:
            printFailure("ERROR: No 'hosts' file in the folder, try creating one manually")

    response = "yes" if auto else query_yes_no("Do you want to update all data sources?")
    if response == "yes" and update:
        updateAllSources()
    else:
        if not auto:
            print ("OK, we\'ll stick with what we\'ve  got locally.")

def promptForExclusions():
    response = "no" if auto else query_yes_no("Do you want to exclude any domains?\n" +
                            "For example, hulu.com video streaming must be able to access " +
                            "its tracking and ad servers in order to play video.")
    if response == "yes":
        displayExclusionOptions()
    else:
        if not auto:
            print ("OK, we\'ll only exclude domains in the whitelist.")

def promptForMoreCustomExclusions():
    response = query_yes_no("Do you have more domains you want to enter?")
    if response == "yes":
        return True
    else:
        return False

def promptForMove(finalFile):

    if replace:
        response = "yes"
    else:
        response = "no" if auto else query_yes_no("Do you want to replace your existing hosts file " +
                            "with the newly generated file?")
    if response == "yes":
        moveHostsFileIntoPlace(finalFile)
    else:
        return False
# End Prompt the User

# Exclusion logic
def displayExclusionOptions():
    for exclusionOption in COMMON_EXCLUSIONS:
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
        domainFromUser = myInput("Enter the domain you want to exclude (e.g. facebook.com): ")
        if isValidDomainFormat(domainFromUser):
            excludeDomain(domainFromUser)
        if promptForMoreCustomExclusions() is False:
            return

def excludeDomain(domain):
    exclusionRegexs.append(re.compile(EXCLUSION_PATTERN + domain))

def matchesExclusions(strippedRule):
    strippedDomain = strippedRule.split()[1]
    for exclusionRegex in exclusionRegexs:
        if exclusionRegex.search(strippedDomain):
            return True
    return False
# End Exclusion Logic

# Update Logic
def updateAllSources():
    allsources = list(set(SOURCES) | set(EXTENSIONS))
    for source in allsources:
        if os.path.isdir(source):
            updateURLs = getUpdateURLsFromFile(source)
            if not len(updateURLs):
                continue

            for updateURL in updateURLs:
                print ("Updating source " + os.path.basename(source) + " from " + updateURL)
                # Cross-python call
                updatedFile = getFileByUrl(updateURL)
                try:
                    updatedFile = updatedFile.replace('\r', '') #get rid of carriage-return symbols
                    # This is cross-python code
                    dataFile = open(os.path.join(DATA_PATH, source, DATA_FILENAMES), 'wb')
                    writeData(dataFile, updatedFile)
                    dataFile.close()
                except:
                    print ("Skipping.")

def getUpdateURLsFromFile(source):
    pathToUpdateFile = os.path.join(DATA_PATH, source, UPDATE_URL_FILENAME)
    if os.path.exists(pathToUpdateFile):
        updateFile = open(pathToUpdateFile, 'r')
        retURLs     = updateFile.readlines()
        # .strip()
        updateFile.close()
    else:
        retURL = None
        printFailure('Warning: Can\'t find the update file for source ' + source + '\n' +
                     'Make sure that there\'s a file at ' + pathToUpdateFile)
    return retURLs
# End Update Logic


def getUpdateURLFromFile(source):
    pathToUpdateFile = os.path.join(DATA_PATH, source, UPDATE_URL_FILENAME)
    if os.path.exists(pathToUpdateFile):
        updateFile = open(pathToUpdateFile, 'r')
        retURL     = updateFile.readline().strip()
        updateFile.close()
    else:
        retURL = None
        printFailure('Warning: Can\'t find the update file for source ' + source + '\n' +
                     'Make sure that there\'s a file at ' + pathToUpdateFile)
    return retURL
# End Update Logic

# File Logic
def createInitialFile():
    mergeFile = tempfile.NamedTemporaryFile()
    for source in SOURCES:
        curFile = open(os.path.join(DATA_PATH, source, DATA_FILENAMES), 'r')
        #Done in a cross-python way
        writeData(mergeFile, curFile.read())

    for source in extensions:
        curFile = open(os.path.join(EXTENSIONS_PATH, source, DATA_FILENAMES), 'r')
        #Done in a cross-python way
        writeData(mergeFile, curFile.read())

    return mergeFile

def removeDupsAndExcl(mergeFile):
    global numberOfRules
    if os.path.isfile(WHITELIST_FILE):
        with open(WHITELIST_FILE, "r") as ins:
            for line in ins:
                if line.rstrip():
                    EXCLUSIONS.append(line)

    if not os.path.exists(outputPath):
        os.makedirs(outputPath)

    # Another mode is required to read and write the file in Python 3
    if Python3:
        finalFile = open(os.path.join(outputPath, 'hosts'), 'w+b')
    else:
        finalFile = open(os.path.join(outputPath, 'hosts'), 'w+')

    mergeFile.seek(0) # reset file pointer
    hostnames = set()
    hostnames.add("localhost")
    hostnames.add("localhost.localdomain")
    hostnames.add("local")
    hostnames.add("broadcasthost")
    for line in mergeFile.readlines():
        write = 'true'
        # Explicit encoding
        line = line.decode("UTF-8")
        # replace tabs with space
        line = line.replace('\t+', ' ')
        # Testing the first character doesn't require startswith
        if line[0] == '#' or re.match(r'^\s*$', line[0]):
            # Cross-python write
            writeData(finalFile, line)
            continue
        if '::1' in line:
            continue

        strippedRule = stripRule(line) #strip comments
        if len(strippedRule) == 0:
            continue
        if matchesExclusions(strippedRule):
            continue
        hostname, normalizedRule = normalizeRule(strippedRule) # normalize rule
        for exclude in EXCLUSIONS:
            if exclude in line:
                write = 'false'
                break
        if normalizedRule and (hostname not in hostnames) and (write == 'true'):
            writeData(finalFile, normalizedRule)
            hostnames.add(hostname)
            numberOfRules += 1

    mergeFile.close()

    return finalFile

def normalizeRule(rule):
    result = re.search(r'^[ \t]*(\d+\.\d+\.\d+\.\d+)\s+([\w\.-]+)(.*)', rule)
    if result:
        hostname, suffix = result.group(2,3)
        hostname = hostname.lower().strip() # explicitly lowercase and trim the hostname
        if suffix is not '':
            # add suffix as comment only, not as a separate host
            return hostname, "%s %s #%s\n" % (targetIP, hostname, suffix)
        else:
            return hostname, "%s %s\n" % (targetIP, hostname)
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
        return ''
    else:
        return splitLine[0] + ' ' + splitLine[1]

def writeOpeningHeader(finalFile):
    global numberOfRules
    finalFile.seek(0) #reset file pointer
    fileContents = finalFile.read()  #save content
    finalFile.seek(0) #write at the top
    writeData(finalFile, '# This hosts file is a merged collection of hosts from reputable sources,\n')
    writeData(finalFile, '# with a dash of crowd sourcing via Github\n#\n')
    writeData(finalFile, '# Date: ' + time.strftime("%B %d %Y", time.gmtime()) + '\n')
    writeData(finalFile, '# Number of unique domains: ' + "{:,}".format(numberOfRules) + '\n#\n')
    writeData(finalFile, '# Fetch the latest version of this file: https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts\n')
    writeData(finalFile, '# Project home page: https://github.com/StevenBlack/hosts\n#\n')
    writeData(finalFile, '# ===============================================================\n')
    writeData(finalFile, '\n')
    writeData(finalFile, '127.0.0.1 localhost\n')
    writeData(finalFile, '127.0.0.1 localhost.localdomain\n')
    writeData(finalFile, '127.0.0.1 local\n')
    writeData(finalFile, '255.255.255.255 broadcasthost\n')
    writeData(finalFile, '::1 localhost\n')
    writeData(finalFile, 'fe80::1%lo0 localhost\n')
    writeData(finalFile, '\n')

    preamble = os.path.join(BASEDIR_PATH, "myhosts")
    if os.path.isfile(preamble):
        with open(preamble, "r") as f:
            writeData(finalFile, f.read())

    finalFile.write(fileContents)

def updateReadme(numberOfRules):
    extensionsStr = "* Extensions: **none**."
    extensionsHeader = ""
    if extensions:
      extensionsStr = "* Extensions: **" + ", ".join(extensions) + "**."
      extensionsHeader = "with "+ ", ".join(extensions) + " extensions"

    with open(os.path.join(outputPath,README_FILENAME), "wt") as out:
        for line in open(README_TEMPLATE):
            line = line.replace( '@GEN_DATE@', time.strftime("%B %d %Y", time.gmtime()))
            line = line.replace( '@EXTENSIONS@', extensionsStr )
            line = line.replace( '@EXTENSIONS_HEADER@', extensionsHeader )
            out.write(line.replace('@NUM_ENTRIES@', "{:,}".format(numberOfRules)))

def moveHostsFileIntoPlace(finalFile):
    if os.name == 'posix':
        dnsFlushOccured = False
        print ("Moving the file requires administrative privileges. " +
               "You might need to enter your password.")
        if subprocess.call(["/usr/bin/sudo", "cp", os.path.abspath(finalFile.name), "/etc/hosts"]):
            printFailure("Moving the file failed.")
        print ("Flushing the DNS Cache to utilize new hosts file...")
        if platform.system() == 'Darwin':
            dnsFlushOccured = True
            if subprocess.call(["/usr/bin/sudo", "killall", "-HUP", "mDNSResponder"]):
                printFailure("Flushing the DNS Cache failed.")
        else:
            if os.path.isfile("/etc/rc.d/init.d/nscd"):
                dnsFlushOccured = True
                if subprocess.call(["/usr/bin/sudo", "/etc/rc.d/init.d/nscd", "restart"]):
                    printFailure("Flushing the DNS Cache failed.")
                else:
                    printSuccess("Flushing DNS by restarting nscd succeeded")
            if os.path.isfile("/usr/lib/systemd/system/NetworkManager.service"):
                dnsFlushOccured = True
                if subprocess.call(["/usr/bin/sudo", "/usr/bin/systemctl", "restart", "NetworkManager.service"]):
                    printFailure("Flushing the DNS Cache failed.")
                else:
                    printSuccess("Flushing DNS by restarting NetworkManager succeeded")
            if os.path.isfile("/usr/lib/systemd/system/wicd.service"):
                dnsFlushOccured = True
                if subprocess.call(["/usr/bin/sudo", "/usr/bin/systemctl", "restart", "wicd.service"]):
                    printFailure("Flushing the DNS Cache failed.")
                else:
                    printSuccess("Flushing DNS by restarting wicd succeeded")
            if os.path.isfile("/usr/lib/systemd/system/dnsmasq.service"):
                dnsFlushOccured = True
                if subprocess.call(["/usr/bin/sudo", "/usr/bin/systemctl", "restart", "dnsmasq.service"]):
                    printFailure("Flushing the DNS Cache failed.")
                else:
                    printSuccess("Flushing DNS by restarting dnsmasq succeeded")
            if not dnsFlushOccured:
                printFailure("Unable to determine DNS management tool.")
    elif os.name == 'nt':
        print ("Automatically moving the hosts file in place is not yet supported.")
        print ("Please move the generated file to %SystemRoot%\system32\drivers\etc\hosts")

def removeOldHostsFile():               # hotfix since merging with an already existing hosts file leads to artefacts and duplicates
    oldFilePath = os.path.join(BASEDIR_PATH, 'hosts')
    open(oldFilePath, 'a').close()        # create if already removed, so remove wont raise an error
    backupFilePath = os.path.join(BASEDIR_PATH, 'hosts-{0}'.format(time.strftime("%Y-%m-%d-%H-%M-%S")))
    shutil.copy(oldFilePath, backupFilePath) # make a backup copy, marking the date in which the list was updated
    os.remove(oldFilePath)
    open(oldFilePath, 'a').close()        # create new empty hostsfile

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
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while 1:
        sys.stdout.write(colorize(question, colors.PROMPT) + prompt)
        # Changed to be cross-python
        choice = myInput().lower()
        if default is not None and choice == '':
            return default
        elif choice in valid.keys():
            return valid[choice]
        else:
            printFailure("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")
## end of http://code.activestate.com/recipes/577058/ }}}

def isValidDomainFormat(domain):
    if domain == '':
        print ("You didn\'t enter a domain. Try again.")
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
    PROMPT  = '\033[94m'
    SUCCESS = '\033[92m'
    FAIL    = '\033[91m'
    ENDC    = '\033[0m'

def colorize(text, color):
    return color + text + colors.ENDC

def printSuccess(text):
    print (colorize(text, colors.SUCCESS))

def printFailure(text):
    print (colorize(text, colors.FAIL))
# End Helper Functions

if __name__ == "__main__":
    main()
