#!/usr/bin/env python

# Script by Steven Black
# https://github.com/StevenBlack
#
# This Python script will update the readme files in this repo.
#
# pylint: disable=invalid-name
# pylint: disable=bad-whitespace

import os
import platform
import string
import sys
import time
import json
from string import Template

# Project Settings
BASEDIR_PATH         = os.path.dirname(os.path.realpath(__file__))
README_TEMPLATE      = os.path.join(BASEDIR_PATH, 'readme_template.md')
README_FILENAME      = 'readme.md'
README_DATA_FILENAME = "readmeData.json"

# Detecting Python 3 for version-dependent implementations
Python3 = sys.version_info >= (3,0)

def main():

    s = Template('${description} | [Readme](https://github.com/StevenBlack/hosts/blob/master/${location}readme.md) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/${location}hosts) | [link](https://raw.githubusercontent.com/StevenBlack/hosts/master/${location}hosts.zip) | ${fmtentries}')

    with open(README_DATA_FILENAME, 'r') as f:
       data = json.load(f)

    if Python3:
        keys = list(data.keys())
    else:
        keys = data.keys()

    keys.sort(key=cmp_keys)
    print (keys)
    tocRows = ""
    for key in keys:
        data[key]["fmtentries"] = "{:,}".format(data[key]["entries"])
        if key == "base":
            data[key]["description"] = 'Unified hosts = **(adware + malware)**'
        else:
            data[key]["description"] = 'Unified hosts **+ ' + key.replace( "-", " + ") + '**'

        tocRows += s.substitute(data[key]) + "\n"

    rowdefaults = {
        "name": "",
        "description": "",
        "homeurl": "",
        "frequency": "",
        "issues": "",
        "url": ""}

    t = Template('${name} | ${description} |[link](${homeurl}) | [raw](${url}) | ${frequency} ')

    for key in keys:
        extensions = key.replace( "-", ", ")
        extensionsStr = "* Extensions: **" + extensions + "**."
        extensionsHeader = "with "+ extensions + " extensions"

        sourceRows = ""
        sourceList = data[key]["sourcesdata"]
        for source in sourceList:
            thisrow = {}
            thisrow.update(rowdefaults)
            thisrow.update(source)
            sourceRows += t.substitute(thisrow) + "\n"

        with open(os.path.join(data[key]["location"],README_FILENAME), "wt") as out:
            for line in open(README_TEMPLATE):
                line = line.replace( '@GEN_DATE@', time.strftime("%B %d %Y", time.gmtime()))
                line = line.replace( '@EXTENSIONS@', extensionsStr )
                line = line.replace( '@EXTENSIONS_HEADER@', extensionsHeader )
                line = line.replace( '@NUM_ENTRIES@', "{:,}".format(data[key]["entries"]))
                line = line.replace( '@SUBFOLDER@',os.path.join(data[key]["location"], ''))
                line = line.replace( '@TOCROWS@', tocRows )
                line = line.replace( '@SOURCEROWS@', sourceRows )
                out.write( line )

def cmp_keys(item):
    return item.count('-'), item

if __name__ == "__main__":
    main()
