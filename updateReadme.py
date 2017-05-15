#!/usr/bin/env python

# Script by Steven Black
# https://github.com/StevenBlack
#
# This Python script will update the readme files in this repo.

import os
import sys
import time
import json
from string import Template

# Project Settings
BASEDIR_PATH = os.path.dirname(os.path.realpath(__file__))
README_TEMPLATE = os.path.join(BASEDIR_PATH, 'readme_template.md')
README_FILENAME = 'readme.md'
README_DATA_FILENAME = "readmeData.json"


def main():

    s = Template('${description} | [Readme](https://github.com/StevenBlack/'
                 'hosts/blob/master/${location}readme.md) | '
                 '[link](https://raw.githubusercontent.com/StevenBlack/'
                 'hosts/master/${location}hosts) | [link]'
                 '(https://raw.githubusercontent.com/StevenBlack/hosts/'
                 'master/${location}hosts.zip) | ${fmtentries} | '
                 '[link](http://sbc.io/hosts/${location}hosts)')

    with open(README_DATA_FILENAME, 'r') as f:
        data = json.load(f)

    if sys.version_info >= (3, 0):
        keys = list(data.keys())
    else:
        keys = data.keys()

    keys.sort(key=cmp_keys)

    toc_rows = ""
    for key in keys:
        data[key]["fmtentries"] = "{:,}".format(data[key]["entries"])
        if key == "base":
            data[key]["description"] = 'Unified hosts = **(adware + malware)**'
        else:
            data[key]["description"] = ('Unified hosts **+ ' +
                                        key.replace("-", " + ") + '**')

        toc_rows += s.substitute(data[key]) + "\n"

    row_defaults = {
        "name": "",
        "description": "",
        "homeurl": "",
        "frequency": "",
        "issues": "",
        "url": ""}

    t = Template('${name} | ${description} |[link](${homeurl})'
                 ' | [raw](${url}) | ${frequency} ')

    for key in keys:
        extensions = key.replace("-", ", ")
        extensions_str = "* Extensions: **" + extensions + "**."
        extensions_header = "with " + extensions + " extensions"

        source_rows = ""
        source_list = data[key]["sourcesdata"]

        for source in source_list:
            this_row = {}
            this_row.update(row_defaults)
            this_row.update(source)
            source_rows += t.substitute(this_row) + "\n"

        with open(os.path.join(data[key]["location"],
                               README_FILENAME), "wt") as out:
            for line in open(README_TEMPLATE):
                line = line.replace('@GEN_DATE@', time.strftime("%B %d %Y",
                                                                time.gmtime()))
                line = line.replace('@EXTENSIONS@', extensions_str)
                line = line.replace('@EXTENSIONS_HEADER@', extensions_header)
                line = line.replace('@NUM_ENTRIES@',
                                    "{:,}".format(data[key]["entries"]))
                line = line.replace('@SUBFOLDER@',
                                    os.path.join(data[key]["location"], ''))
                line = line.replace('@TOCROWS@', toc_rows)
                line = line.replace('@SOURCEROWS@', source_rows)
                out.write(line)


def cmp_keys(item):
    return item.count('-'), item


if __name__ == "__main__":
    main()
