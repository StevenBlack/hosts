#!/usr/bin/env python

# Script by Ben Limmer
# https://github.com/l1m5
#
# This simple Python script will combine all the host files you provide
# as sources into one, unique host file to keep you internet browsing happy.

import os
import platform
import re
import string
import subprocess
import sys
import tempfile
import __future__

from future.standard_library import install_aliases
from builtins import input
install_aliases()

import urllib.request, urllib.error, urllib.parse
import zipfile
import io

# Project Settings
BASEDIR_PATH = os.path.dirname(os.path.realpath(__file__))
DATA_PATH = BASEDIR_PATH + '/data'
DATA_FILENAMES = 'hosts'
UPDATE_URL_FILENAME = 'update.info'
SOURCES = os.listdir(DATA_PATH)
README_TEMPLATE = BASEDIR_PATH + '/readme_template.md'
README_FILE = BASEDIR_PATH + '/readme.md'
TARGET_HOST = '0.0.0.0'

# Exclusions
EXCLUSION_PATTERN = '([a-zA-Z\d-]+\.){0,}' #append domain the end

# Common domains to exclude
COMMON_EXCLUSIONS = ['hulu.com']

# Global vars
exclusionRegexs = []
numberOfRules = 0

def main():
	promptForUpdate()
	promptForExclusions()
	mergeFile = createInitialFile()
	finalFile = removeDups(mergeFile)
	finalizeFile(finalFile)
	updateReadme(numberOfRules)
	printSuccess('Success! Your shiny new hosts file has been prepared.\nIt contains ' + str(numberOfRules) + ' unique entries.')
	promptForMove(finalFile)

# Prompt the User
def promptForUpdate():
	response = query_yes_no("Do you want to update all data sources?")
	if (response == "yes"):
		updateAllSources()
	else:
		print('OK, we\'ll stick with what we\'ve  got locally.')

def promptForExclusions():
	response = query_yes_no("Do you want to exclude any domains?\n" +
							"For example, hulu.com video streaming must be able to access " +
							"its tracking and ad servers in order to play video.")
	if (response == "yes"):
		displayExclusionOptions()
	else:
		print('OK, we won\'t exclude any domains.')

def promptForMoreCustomExclusions():
	response = query_yes_no("Do you have more domains you want to enter?")
	if (response == "yes"):
		return True
	else:
		return False

def promptForMove(finalFile):
  response = query_yes_no("Do you want to replace your existing hosts file with the newly generated file?")
  if (response == "yes"):
    moveHostsFileIntoPlace(finalFile)
  else:
    return False
# End Prompt the User

# Exclusion logic
def displayExclusionOptions():
	for exclusionOption in COMMON_EXCLUSIONS:
		response = query_yes_no("Do you want to exclude the domain " + exclusionOption + " ?")
		if (response == "yes"):
			excludeDomain(exclusionOption)
		else:
			continue
	response = query_yes_no("Do you want to exclude any other domains?")
	if (response == "yes"):
		gatherCustomExclusions()

def gatherCustomExclusions():
	while True:
		domainFromUser = input("Enter the domain you want to exclude (e.g. facebook.com): ")
		if (isValidDomainFormat(domainFromUser)):
			excludeDomain(domainFromUser)
		if (promptForMoreCustomExclusions() == False):
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
	for source in SOURCES:
		updateURL = getUpdateURLFromFile(source)
		if (updateURL == None):
			continue;
		print('Updating source ' + source + ' from ' + updateURL)
		updatedFile = urllib.request.urlopen(updateURL)

		updatedFile = updatedFile.read()

		if '.zip' in updateURL:
			updatedZippedFile = zipfile.ZipFile(io.StringIO(updatedFile))
			for name in updatedZippedFile.namelist():
				if name in ('hosts', 'hosts.txt'):
					updatedFile = updatedZippedFile.open(name).read()
					break

		updatedFile = updatedFile.decode('utf-8').replace('\r', '' ) #get rid of carriage-return symbols

		dataFile   = open(DATA_PATH + '/' + source + '/' + DATA_FILENAMES, 'w')
		dataFile.write(updatedFile)
		dataFile.close()


def getUpdateURLFromFile(source):
	pathToUpdateFile = DATA_PATH + '/' + source + '/' + UPDATE_URL_FILENAME
	if os.path.exists(pathToUpdateFile):
		updateFile = open(pathToUpdateFile, 'r')
		retURL = updateFile.readline().strip()
		updateFile.close()
	else:
		retURL = None
		printFailure('Warning: Can\'t find the update file for source ' + source + '\n' +
					 'Make sure that there\'s a file at ' + pathToUpdateFile)
	return retURL
# End Update Logic

# File Logic
def createInitialFile():
	mergeFile = tempfile.NamedTemporaryFile('wt+')
	for source in SOURCES:
		curFile = open(DATA_PATH + '/' + source +'/' + DATA_FILENAMES, 'r')
		mergeFile.write('\n# Begin ' + source + '\n')
		mergeFile.write(curFile.read())
		mergeFile.write('\n# End ' + source + '\n')
	return mergeFile

def removeDups(mergeFile):
	global numberOfRules

	finalFile = open(BASEDIR_PATH + '/hosts', 'w+t')
	mergeFile.seek(0) # reset file pointer

	hostnames = set()
	for line in mergeFile.readlines():
		if line[0].startswith("#") or re.match(r'^\s*$', line[0]):
			finalFile.write(line) #maintain the comments for readability
			continue
		strippedRule = stripRule(line) #strip comments
		if matchesExclusions(strippedRule):
			continue
		hostname, normalizedRule = normalizeRule(strippedRule) # normalize rule

		if normalizedRule and hostname not in hostnames:
			finalFile.write(normalizedRule)
			hostnames.add(hostname)
			numberOfRules += 1
		else:
			finalFile.write(line)

	mergeFile.close()

	return finalFile

def normalizeRule(rule):
	result = re.search(r'^\s*(\d+\.\d+\.\d+\.\d+)\s+([\w\.-]+)(.*)',rule)
	if result:
		target, hostname, suffix = result.groups()
		return hostname, "%s\t%s%s\n" % (TARGET_HOST, hostname, suffix)
	print('==>%s<==' % rule)
	return None, None

def finalizeFile(finalFile):
	writeOpeningHeader(finalFile)
	finalFile.close()

# Some sources put comments around their rules, for accuracy we need to strip them
# the comments are preserved in the output hosts file
def stripRule(line):
	splitLine = line.split()
	if (len(splitLine) < 2) :
		printFailure('A line in the hostfile is going to cause problems because it is nonstandard\n' +
					 'The line reads ' + line + ' please check your data files. Maybe you have a comment without a #?')
		sys.exit()
	return splitLine[0] + ' ' + splitLine[1]

def writeOpeningHeader(finalFile):
	global numberOfRules
	finalFile.seek(0) #reset file pointer
	fileContents = finalFile.read(); #save content
	finalFile.seek(0) #write at the top
	finalFile.write('# This file is a merged collection of hosts from reputable sources,\n')
	finalFile.write('# with a dash of crowd sourcing via Github\n#\n')
	finalFile.write('# Project home page: https://github.com/StevenBlack/hosts\n#\n')
	finalFile.write('# Current sources:\n')
	for source in SOURCES:
		finalFile.write('#    ' + source + '\n')
	finalFile.write('#\n')
	finalFile.write('# Merging these sources produced ' + str(numberOfRules) + ' unique entries\n')
	finalFile.write('# ===============================================================\n')
	finalFile.write(fileContents)

def updateReadme(numberOfRules):
	with open(README_FILE, "wt") as out:
		for line in open(README_TEMPLATE):
			out.write(line.replace('@NUM_ENTRIES@', str(numberOfRules)))

def moveHostsFileIntoPlace(finalFile):
	if (os.name == 'posix'):
		print('Moving the file requires administrative privileges. You might need to enter your password.')
		if(subprocess.call(["/usr/bin/sudo", "cp", os.path.abspath(finalFile.name), "/etc/hosts"])):
			printFailure("Moving the file failed.")
		print('Flushing the DNS Cache to utilize new hosts file...')
		if (platform.system() == 'Darwin'):
			if(subprocess.call(["/usr/bin/sudo", "killall", "-HUP", "mDNSResponder"])):
				printFailure("Flushing the DNS Cache failed.")
		else:
			if(subprocess.call(["/usr/bin/sudo", "/etc/rc.d/init.d/nscd", "restart"])):
				printFailure("Flushing the DNS Cache failed.")
	elif (os.name == 'nt'):
		print('Automatically moving the hosts file in place is not yet supported.')
		print('Please move the generated file to %SystemRoot%\system32\drivers\etc\hosts')

# End File Logic

# Helper Functions
## {{{ http://code.activestate.com/recipes/577058/ (r2)
def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes":"yes",   "y":"yes",  "ye":"yes",
             "no":"no",     "n":"no"}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while 1:
        sys.stdout.write(colorize(question, colors.PROMPT) + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return default
        elif choice in list(valid.keys()):
            return valid[choice]
        else:
            printFailure("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")
## end of http://code.activestate.com/recipes/577058/ }}}

def isValidDomainFormat(domain):
	if (domain == ''):
		print("You didn\'t enter a domain. Try again.")
		return False
	domainRegex = re.compile("www\d{0,3}[.]|https?")
	if (domainRegex.match(domain)):
		print("The domain " + domain + " is not valid. Do not include www.domain.com or http(s)://domain.com. Try again.")
		return False
	else:
		return True

# Colors
class colors:
    PROMPT 	= '\033[94m'
    SUCCESS = '\033[92m'
    FAIL 	= '\033[91m'
    ENDC 	= '\033[0m'

def colorize(text, color):
	return color + text + colors.ENDC

def printSuccess(text):
	print(colorize(text, colors.SUCCESS))

def printFailure(text):
	print(colorize(text, colors.FAIL))
# End Helper Functions

if __name__ == "__main__":
	main()
