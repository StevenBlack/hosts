#!/usr/bin/env python

# Script by Steven Black
# https://github.com/StevenBlack
#
# This Python script will update the readme files in this repo.

from string import Template

import os
import sys
import time
import json

# Project Settings
BASEDIR_PATH = os.path.dirname(os.path.realpath(__file__))
README_TEMPLATE = os.path.join(BASEDIR_PATH, 'readme_template.md')
README_FILENAME = 'readme.md'
README_DATA_FILENAME = "readmeData.json"

# Detecting Python 3 for version-dependent implementations
PY3 = sys.version_info >= (3, 0)


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

    if PY3:
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
                line = line.replace('@EXTENSIONS@',
                                    decode_line(extensions_str))
                line = line.replace('@EXTENSIONS_HEADER@',
                                    decode_line(extensions_header))
                line = line.replace('@NUM_ENTRIES@',
                                    "{:,}".format(data[key]["entries"]))
                line = line.replace('@SUBFOLDER@',
                                    decode_line(os.path.join(
                                        data[key]["location"], '')))
                line = line.replace('@TOCROWS@',
                                    decode_line(toc_rows))
                line = line.replace('@SOURCEROWS@',
                                    decode_line(source_rows))
                out.write(decode_line(line))


def decode_line(line):
    """
    Python 2 compatible method for decoding unicode lines.

    Parameters
    ----------
    line : str
        The unicode string to decode.

    Returns
    -------
    decoded_str : str
        Decoded unicode string.
    """

    # Python 3.x has no unicode issues.
    if PY3:
        return line

    # The biggest Python 2.x compatibility issue is the decoding of the
    # en-dash. It either takes the form of u"\u2013" or "\xe2\x80\x93."
    #
    # This attempts to convert "\xe2\x80\x93" to u"\u2013" if necessary.
    # If the character is already in the form of u"\u2013," this will
    # raise an UnicodeEncodeError.
    #
    # In general, this line of code will allow us to convert unicode,
    # UTF-8 encoded characters into pure unicode.
    try:
        line = line.decode("UTF-8")
    except UnicodeEncodeError:
        pass

    # Replace u"\u2013" with the en-dash, so we now can decode.
    #
    # We can add additional "replace" lines in case there are other unicode
    # literals that Python 2.x cannot handle.
    line = line.replace(u"\u2013", "-")
    return str(line.decode("UTF-8"))


def cmp_keys(item):
    return item.count('-'), item


if __name__ == "__main__":
    main()
