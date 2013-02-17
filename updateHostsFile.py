#!/usr/bin/env python

# Script by Ben Limmer
# https://github.com/l1m5
#
# This simple Python script will combine all the host files you provide
# as sources into one, unique host file to keep you internet browsing happy.

import os
import re
import string
import sys
import tempfile
import urllib2

# Project Settings
BASEDIR_PATH = os.path.dirname(os.path.realpath(__file__))
DATA_PATH = BASEDIR_PATH + '/data'
DATA_FILENAMES = 'hosts'
UPDATE_URL_FILENAME = 'update.info'
SOURCES = os.listdir(DATA_PATH)

# Exclusions
EXCLUSION_PATTERN = '([a-zA-Z\d-]+\.){0,}' #append domain the end

# Common domains to exclude
COMMON_EXCLUSIONS = ['hulu.com']

# Global vars
exclusionRegexs = []
duplicatesRemoved = 0;

def main():
	promptForUpdate()
	promptForExclusions()
	mergeFile = createInitialFile()
	finalFile = removeDups(mergeFile)
	finalizeFile(finalFile)
	print 'Success! Your shiny new hosts file has been prepared.'

# Prompt the User
def promptForUpdate():
	response = query_yes_no("Do you want to update all data sources?")
	if (response == "yes"):
		updateAllSources()
	else:
		print 'OK, we\'ll stick with what we\'ve  got locally.'

def promptForExclusions():
	response = query_yes_no("Do you want to exclude any domains?\n" +
							"For example, hulu.com video streaming must be able to access " +
							"its tracking and ad servers in order to play video.")
	if (response == "yes"):
		displayExclusionOptions()
	else:
		print 'OK, we won\'t exclude any domains.'
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
	moreEntries = True;
	while (moreEntries):
		domainFromUser = raw_input("Enter the domain you want to exclude (e.g. facebook.com): ")
		if (isValidDomainFormat(domainFromUser)):
			excludeDomain(domainFromUser)
		response = query_yes_no("Do you have more domains you want to enter?")
        if (response == "no"):
        	moreEntries = False

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
		print 'Updating source ' + source + ' from ' + updateURL
		updatedFile = urllib2.urlopen(updateURL)
		updatedFile = updatedFile.read()
		updatedFile = string.replace( updatedFile, '\r', '' ) #get rid of carriage-return symbols

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
		print 'Warning: Can\'t find the update file for source ' + source
		print 'Make sure that there\'s a file at ' + pathToUpdateFile
	return retURL
# End Update Logic

# File Logic
def createInitialFile():
	mergeFile = tempfile.NamedTemporaryFile()
	for source in SOURCES:
		curFile = open(DATA_PATH + '/' + source +'/' + DATA_FILENAMES, 'r')
		mergeFile.write('\n# Begin ' + source + '\n')
		mergeFile.write(curFile.read())
		mergeFile.write('\n# End ' + source + '\n')
	return mergeFile

def removeDups(mergeFile):
	global duplicatesRemoved
	finalFile = open(BASEDIR_PATH + '/hosts', 'w+b')
	mergeFile.seek(0) # reset file pointer

	rules_seen = set()
	for line in mergeFile.readlines():
		if line[0].startswith("#") or line[0] == '\n':
			finalFile.write(line) #maintain the comments for readability
			continue
		strippedRule = stripRule(line) #strip comments
		if matchesExclusions(strippedRule):
			continue
		if strippedRule not in rules_seen:
			finalFile.write(line)
			rules_seen.add(strippedRule)
		else:
			duplicatesRemoved += 1

	mergeFile.close()

	print 'Removed ' + str(duplicatesRemoved) + ' duplicates from the merged file'
	return finalFile

def finalizeFile(finalFile):
	writeOpeningHeader(finalFile)
	finalFile.close()

# Some sources put comments around their rules, for accuracy we need to strip them
# the comments are preserved in the output hosts file
def stripRule(line):
	splitLine = line.split()
	if (len(splitLine) < 2) :
		print 'A line in the hostfile is going to cause problems because it is nonstandard'
		print 'The line reads ' + line + ' please check your data files. Maybe you have a comment without a #?'
		sys.exit()
	return splitLine[0] + ' ' + splitLine[1]

def writeOpeningHeader(finalFile):
	global duplicatesRemoved
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
	finalFile.write('# Take Note:\n')
	finalFile.write('# Merging these sources produced ' + str(duplicatesRemoved) + ' duplicates\n')
	finalFile.write('# ===============================================================\n')
	finalFile.write(fileContents)
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
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return default
        elif choice in valid.keys():
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")
## end of http://code.activestate.com/recipes/577058/ }}}

def isValidDomainFormat(domain):
	domainRegex = re.compile("www\d{0,3}[.]|https?")
	if (domainRegex.match(domain)):
		print "The domain " + domain + " is not valid. Do not include www.domain.com or http(s)://domain.com. Try again."
		return False
	else:
		return True
# End Helper Functions

if __name__ == "__main__":
	main()