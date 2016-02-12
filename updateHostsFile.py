#!/usr/bin/env python
# coding: utf-8

# Script by Ben Limmer
# https://github.com/l1m5
#
# Output traduzido por Gabriel Antunes
# https://github.com/muthdra
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
import string
import subprocess
import sys
import tempfile
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
        print ("Erro ao abrir arquivo: ", url)
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
DATA_FILENAMES      = 'hosts'
UPDATE_URL_FILENAME = 'update.info'
SOURCES             = listdir_nohidden(DATA_PATH)
README_TEMPLATE     = os.path.join(BASEDIR_PATH, 'readme_template.md')
README_FILE         = os.path.join(BASEDIR_PATH, 'readme.md')
TARGET_HOST         = '0.0.0.0'
WHITELIST_FILE      = os.path.join(BASEDIR_PATH, 'whitelist')

# Exclusions
EXCLUSION_PATTERN = '([a-zA-Z\d-]+\.){0,}' #append domain the end
EXCLUSIONS        = []
# Common domains to exclude
COMMON_EXCLUSIONS = ['hulu.com']

# Global vars
exclusionRegexs = []
numberOfRules   = 0

auto = False

def main():
    parser = argparse.ArgumentParser(description="Cria um arquivo de hosts mesclado dos hosts guardados nas subpastas da pasta data.")
    parser.add_argument("--auto", "-a", dest="auto", default=False, action='store_true', help="Rodar sem prompts.")
    args = parser.parse_args()

    global auto
    auto = args.auto

    promptForUpdate()
    promptForExclusions()
    mergeFile = createInitialFile()
    removeOldHostsFile()
    finalFile = removeDupsAndExcl(mergeFile)
    finalizeFile(finalFile)
    updateReadme(numberOfRules)
    printSuccess("Sucesso! O seu novo arquivo de hosts foi preparado.\nEle contém " +
                 "{:,}".format(numberOfRules) + " entradas únicas.")

    promptForMove(finalFile)

# Prompt the User
def promptForUpdate():
    # Create hosts file if it doesn't exists
    if not os.path.isfile(os.path.join(BASEDIR_PATH, 'hosts')):
        try:
            open(os.path.join(BASEDIR_PATH, 'hosts'), 'w+').close()
        except:
            printFailure("ERRO: Arquivo 'hosts' não encontrado na pasta, tente criar um manualmente")

    response = "yes" if auto else query_yes_no("Você deseja atualizar todas as fontes de dados?")
    if response == "yes":
        updateAllSources()
    else:
        print ("OK, vamos nos manter com os arquivos locais.")

def promptForExclusions():
    response = "no" if auto else query_yes_no("Você deseja excluir algum domínio?\n" +
                            "Por exemplo, o site hulu.com precisa acessar " +
                            "seus serviços de propaganda para reproduzir vídeos.")
    if response == "yes":
        displayExclusionOptions()
    else:
        print ("OK, excluiremos apenas os domínios da whitelist.")

def promptForMoreCustomExclusions():
    response = query_yes_no("Você deseja excluir mais domínios?")
    if response == "yes":
        return True
    else:
        return False

def promptForMove(finalFile):
    response = "no" if auto else query_yes_no("Você deseja substituir seu arquivo de hosts existente " +
                                              "pelo novo arquivo gerado?")
    if response == "yes":
        moveHostsFileIntoPlace(finalFile)
    else:
        return False
# End Prompt the User

# Exclusion logic
def displayExclusionOptions():
    for exclusionOption in COMMON_EXCLUSIONS:
        response = query_yes_no("Você deseja excluir o domínio " + exclusionOption + " ?")
        if response == "yes":
            excludeDomain(exclusionOption)
        else:
            continue
    response = query_yes_no("Você deseja excluir outros domínios?")
    if response == "yes":
        gatherCustomExclusions()

def gatherCustomExclusions():
    while True:
        # Cross-python Input
        domainFromUser = myInput("Digite o site que deseja excluir (e.g. facebook.com): ")
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
    for source in SOURCES:
        updateURL = getUpdateURLFromFile(source)
        if updateURL is None:
            continue
        print ("Atualizando fonte " + source + " de " + updateURL)
        # Cross-python call
        updatedFile = getFileByUrl(updateURL)

        try:
            updatedFile = updatedFile.replace('\r', '') #get rid of carriage-return symbols
            # This is cross-python code
            dataFile = open(os.path.join(DATA_PATH, source, DATA_FILENAMES), 'wb')
            writeData(dataFile, updatedFile)
            dataFile.close()
        except:
            print ("Ignorando.")


def getUpdateURLFromFile(source):
    pathToUpdateFile = os.path.join(DATA_PATH, source, UPDATE_URL_FILENAME)
    if os.path.exists(pathToUpdateFile):
        updateFile = open(pathToUpdateFile, 'r')
        retURL     = updateFile.readline().strip()
        updateFile.close()
    else:
        retURL = None
        printFailure('Atenção: Arquivo fonte não encontrado a partir de ' + source + '\n' +
                     'Certifique-se de que existe um arquivo em ' + pathToUpdateFile)
    return retURL
# End Update Logic

# File Logic
def createInitialFile():
    mergeFile = tempfile.NamedTemporaryFile()
    for source in SOURCES:
        curFile = open(os.path.join(DATA_PATH, source, DATA_FILENAMES), 'r')
        #Done in a cross-python way
        writeData(mergeFile, curFile.read())

    return mergeFile

def removeDupsAndExcl(mergeFile):
    global numberOfRules
    if os.path.isfile(WHITELIST_FILE):
        with open(WHITELIST_FILE, "r") as ins:
            for line in ins:
                EXCLUSIONS.append(line)

    # Another mode is required to read and write the file in Python 3
    finalFile = open(os.path.join(BASEDIR_PATH, 'hosts'), 'r+b')
    mergeFile.seek(0) # reset file pointer

    hostnames = set()
    hostnames.add("localhost")
    for line in mergeFile.readlines():
        write = 'true'
        # Explicit encoding
        line = line.decode("UTF-8")
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
        hostname = hostname.lower() # explicitly lowercase hostname
        if suffix is not '':
            # add suffix as comment only, not as a separate host
            return hostname, "%s %s #%s\n" % (TARGET_HOST, hostname, suffix)
        else:
            return hostname, "%s %s\n" % (TARGET_HOST, hostname)
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
    writeData(finalFile, '# Este arquivo e uma mescla de hosts de fontes confiaveis,\n')
    writeData(finalFile, '# com uma pitada de colaboracao do Github\n#\n')
    writeData(finalFile, '# Pagina do projeto: https://github.com/StevenBlack/hosts\n#\n')
    writeData(finalFile, '# Traduzido por Gabriel Antunes: https://github.com/muthdra\n#\n')
    writeData(finalFile, '# ===============================================================\n')
    writeData(finalFile, '\n')
    writeData(finalFile, '127.0.0.1 localhost\n')
    writeData(finalFile, '::1 localhost\n')
    writeData(finalFile, '\n')

    preamble = os.path.join(BASEDIR_PATH, "myhosts")
    if os.path.isfile(preamble):
        with open(preamble, "r") as f:
            writeData(finalFile, f.read())

    finalFile.write(fileContents)

def updateReadme(numberOfRules):
    with open(README_FILE, "wt") as out:
        for line in open(README_TEMPLATE):
            out.write(line.replace('@NUM_ENTRIES@', "{:,}".format(numberOfRules)))

def moveHostsFileIntoPlace(finalFile):
    if os.name == 'posix':
        print ("Privilégios de administrador são necessários para mover o arquivo. " +
               "Talvez você precise digitar sua senha.")
        if subprocess.call(["/usr/bin/sudo", "cp", os.path.abspath(finalFile.name), "/etc/hosts"]):
            printFailure("Moving the file failed.")
        print ("Limpando o Cache DNS para utilizar o novo arquivo de hosts...")
        if platform.system() == 'Darwin':
            if subprocess.call(["/usr/bin/sudo", "killall", "-HUP", "mDNSResponder"]):
                printFailure("A limpeza do Cache DNS falhou.")
        else:
            if os.path.isfile("/etc/rc.d/init.d/nscd"):
                if subprocess.call(["/usr/bin/sudo", "/etc/rc.d/init.d/nscd", "restart"]):
                    printFailure("Flushing the DNS Cache failed.")
            if os.path.isfile("/usr/lib/systemd/system/NetworkManager.service"):
                if subprocess.call(["/usr/bin/sudo", "/usr/bin/systemctl", "restart", "NetworkManager.service"]):
                    printFailure("A limpeza do Cache DNS falhou.")

    elif os.name == 'nt':
        print ("Mover automaticamente o arquivo de hosts ainda não é suportado.")
        print ("Por favor mova o arquivo gerado para %SystemRoot%\system32\drivers\etc\hosts")

def removeOldHostsFile():               # hotfix since merging with an already existing hosts file leads to artefacts and duplicates
    oldFilePath = os.path.join(BASEDIR_PATH, 'hosts')
    open(oldFilePath, 'a').close()        # create if already removed, so remove wont raise an error
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
            printFailure("Por favor responda com 'yes' para SIM ou 'no' para NÃO "\
                             "(ou 'y' ou 'n').\n")
## end of http://code.activestate.com/recipes/577058/ }}}

def isValidDomainFormat(domain):
    if domain == '':
        print ("Você não digitou um domínio. Tente novamente")
        return False
    domainRegex = re.compile("www\d{0,3}[.]|https?")
    if domainRegex.match(domain):
        print ("O domínio " + domain + " não é válido. " +
               "Não inclua www.domain.com ou http(s)://domain.com. Tente novamente.")
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
