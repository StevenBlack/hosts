#!/usr/bin/env python

# Script by gfyoung
# https://github.com/gfyoung
#
# This Python script will generate hosts files and update the readme file.

from __future__ import print_function

import argparse
import subprocess
import sys


def print_failure(msg):
    """
    Print a failure message.

    Parameters
    ----------
    msg : str
        The failure message to print.
    """

    print("\033[91m" + msg + "\033[0m")


def update_hosts_file(*flags):
    """
    Wrapper around running updateHostsFile.py

    Parameters
    ----------
    flags : varargs
        Commandline flags to pass into updateHostsFile.py. For more info, run
        the following command in the terminal or command prompt:

        ```
        python updateHostsFile.py -h
        ```
    """

    if subprocess.call([sys.executable, "updateHostsFile.py"] + list(flags)):
        print_failure("Failed to update hosts file")


def update_readme_file():
    """
    Wrapper around running updateReadme.py
    """

    if subprocess.call([sys.executable, "updateReadme.py"]):
        print_failure("Failed to update readme file")

def recursively_loop_extensions(extension, extensions, current_extensions):
    """
    Helper function that recursively calls itself to prevent manually creating
    all possible combinations of extensions.

    Will call update_hosts_file for all combinations of extensions
    """
    c_extensions = extensions.copy()
    c_current_extensions = current_extensions.copy()
    c_current_extensions.append(extension)

    name = "-".join(c_current_extensions)

    params = ("-a", "-n", "-o", "alternates/"+name, "-e") + tuple(c_current_extensions)
    update_hosts_file(*params)

    while len(c_extensions) > 0:
        recursively_loop_extensions(c_extensions.pop(0), c_extensions, c_current_extensions)


def main():
    parser = argparse.ArgumentParser(
        description="Creates custom hosts "
        "file from hosts stored in "
        "data subfolders."
    )
    parser.parse_args()

    # Update the unified hosts file
    update_hosts_file("-a")

    # List of extensions we want to generate, we will loop over them recursively to prevent manual definitions
    # Only add new extensions to the end of the array, to avoid relocating existing hosts-files
    extensions = ["fakenews", "gambling", "porn", "social"]

    while len(extensions) > 0:
        recursively_loop_extensions(extensions.pop(0), extensions, [])

    # Update the readme files.
    update_readme_file()


if __name__ == "__main__":
    main()
