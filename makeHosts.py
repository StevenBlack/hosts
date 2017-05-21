#!/usr/bin/env python

# Script by gfyoung
# https://github.com/gfyoung
#
# This Python script will generate hosts files and update the readme file.

from __future__ import print_function

import sys
import argparse
import subprocess


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


def main():
    parser = argparse.ArgumentParser(description="Creates custom hosts "
                                                 "file from hosts stored in "
                                                 "data subfolders.")
    parser.parse_args()

    update_hosts_file("-a", "-z", "-o",
                      "alternates/gambling",
                      "-e", "gambling")
    update_hosts_file("-a", "-z", "-n", "-o",
                      "alternates/porn",
                      "-e", "porn")
    update_hosts_file("-a", "-z", "-n", "-o",
                      "alternates/social",
                      "-e", "social")
    update_hosts_file("-a", "-z", "-n", "-o",
                      "alternates/fakenews",
                      "-e", "fakenews")

    update_hosts_file("-a", "-z", "-n", "-o",
                      "alternates/fakenews-gambling",
                      "-e", "fakenews", "gambling")
    update_hosts_file("-a", "-z", "-n", "-o",
                      "alternates/fakenews-porn",
                      "-e", "fakenews", "porn")
    update_hosts_file("-a", "-z", "-n", "-o",
                      "alternates/fakenews-social",
                      "-e", "fakenews", "social")
    update_hosts_file("-a", "-z", "-n", "-o",
                      "alternates/gambling-porn",
                      "-e", "gambling", "porn")
    update_hosts_file("-a", "-z", "-n", "-o",
                      "alternates/gambling-social",
                      "-e", "gambling", "social")
    update_hosts_file("-a", "-z", "-n", "-o",
                      "alternates/porn-social",
                      "-e", "porn", "social")

    update_hosts_file("-a", "-z", "-n", "-o",
                      "alternates/fakenews-gambling-porn",
                      "-e", "fakenews", "gambling", "porn")
    update_hosts_file("-a", "-z", "-n", "-o",
                      "alternates/fakenews-gambling-social",
                      "-e", "fakenews", "gambling", "social")
    update_hosts_file("-a", "-z", "-n", "-o",
                      "alternates/fakenews-porn-social",
                      "-e", "fakenews", "porn", "social")
    update_hosts_file("-a", "-z", "-n", "-o",
                      "alternates/gambling-porn-social",
                      "-e", "gambling", "porn", "social")

    update_hosts_file("-a", "-z", "-n", "-o",
                      "alternates/fakenews-gambling-porn-social",
                      "-e", "fakenews", "gambling", "porn", "social")

    update_hosts_file("-a", "-z", "-n")

    # Update the readme files.
    update_readme_file()


if __name__ == "__main__":
    main()
