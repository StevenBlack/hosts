#!/usr/bin/env python

# Script by Steven Black
# https://github.com/StevenBlack
#
# This Python script will update the readme files in this repo.

import json
import os
import time
from string import Template

# Project Settings
BASEDIR_PATH = os.path.dirname(os.path.realpath(__file__))
README_TEMPLATE = os.path.join(BASEDIR_PATH, "readme_template.md")
README_FILENAME = "readme.md"
README_DATA_FILENAME = "readmeData.json"


def main():
    s = Template(
        "${description} | [Readme](https://github.com/StevenBlack/"
        "hosts/blob/master/${location}readme.md) | "
        "[link](https://raw.githubusercontent.com/StevenBlack/"
        "hosts/master/${location}hosts) | "
        "${fmtentries} | "
        "[link](http://sbc.io/hosts/${location}hosts)"
    )
    with open(README_DATA_FILENAME, "r", encoding="utf-8", newline="\n") as f:
        data = json.load(f)

    keys = list(data.keys())

    # Sort by the number of en-dashes in the key
    # and then by the key string itself.
    keys.sort(key=lambda item: (item.count("-"), item))

    toc_rows = ""
    for key in keys:
        data[key]["fmtentries"] = "{:,}".format(data[key]["entries"])
        if key == "base":
            data[key]["description"] = "Unified hosts = **(adware + malware)**"
        else:
            data[key]["description"] = (
                "Unified hosts **+ " + key.replace("-", " + ") + "**"
            )

        if "\\" in data[key]["location"]:
            data[key]["location"] = data[key]["location"].replace("\\", "/")

        toc_rows += s.substitute(data[key]) + "\n"

    row_defaults = {
        "name": "",
        "description": "",
        "homeurl": "",
        "url": "",
        "license": "",
        "issues": "",
    }

    t = Template(
        "${name} | ${description} |[link](${homeurl})"
        " | [raw](${url}) | ${license} | [issues](${issues})"
    )

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

        with open(
            os.path.join(data[key]["location"], README_FILENAME),
            "wt",
            encoding="utf-8",
            newline="\n",
        ) as out:
            for line in open(README_TEMPLATE, encoding="utf-8", newline="\n"):
                line = line.replace(
                    "@GEN_DATE@", time.strftime("%B %d %Y", time.gmtime())
                )
                line = line.replace("@EXTENSIONS@", extensions_str)
                line = line.replace("@EXTENSIONS_HEADER@", extensions_header)
                line = line.replace(
                    "@NUM_ENTRIES@", "{:,}".format(data[key]["entries"])
                )
                line = line.replace(
                    "@SUBFOLDER@", os.path.join(data[key]["location"], "")
                )
                line = line.replace("@TOCROWS@", toc_rows)
                line = line.replace("@SOURCEROWS@", source_rows)
                out.write(line)


if __name__ == "__main__":
    main()
