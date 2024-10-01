#!/usr/bin/env python3

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
    keys.sort(key=lambda item: (item.replace("-only", "").count("-"), item.replace("-only", "")))

    toc_rows = ""
    for key in keys:
        data[key]["fmtentries"] = "{:,}".format(data[key]["entries"])
        if key == "base":
            data[key]["description"] = "Unified hosts = **(adware + malware)**"
        else:
            if data[key]["no_unified_hosts"]:
                data[key]["description"] = (
                    "**" + key.replace("-only", "").replace("-", " + ") + "**"
                )
            else:
                data[key]["description"] = (
                    "Unified hosts **+ " + key.replace("-", " + ") + "**"
                )

        if "\\" in data[key]["location"]:
            data[key]["location"] = data[key]["location"].replace("\\", "/")

        toc_rows += s.substitute(data[key]) + "\n"

    row_defaults = {
        "name": "",
        "homeurl": "",
        "url": "",
        "license": "",
        "issues": "",
        "description": "",
    }

    t = Template(
        "${name} |[link](${homeurl})"
        " | [raw](${url}) | ${license} | [issues](${issues})| ${description}"
    )
    size_history_graph = "![Size history](https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts_file_size_history.png)"
    for key in keys:
        extensions = key.replace("-only", "").replace("-", ", ")
        extensions_str = "* Extensions: **" + extensions + "**."
        if data[key]["no_unified_hosts"]:
            extensions_header = "Limited to the extensions: " + extensions
        else:
            extensions_header = "Unified hosts file with " + extensions + " extensions"

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
                line = line.replace("@SIZEHISTORY@", size_history_graph)
                out.write(line)


if __name__ == "__main__":
    main()
