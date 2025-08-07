#!/usr/bin/env python3

# Script by Ben Limmer
# https://github.com/l1m5
#
# This Python script will combine all the host files you provide
# as sources into one, unique host file to keep your internet browsing happy.

import argparse
import fnmatch
import ipaddress
import json
import locale
import os
import platform
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from glob import glob
from typing import Optional, Tuple

# Detecting Python 3 for version-dependent implementations
PY3 = sys.version_info >= (3, 0)

if not PY3:
    raise Exception("We do not support Python 2 anymore.")


try:
    import requests
except ImportError:
    raise ImportError(
        "This project's dependencies have changed. The Requests library ("
        "https://docs.python-requests.org/en/latest/) is now required."
    )


# Syntactic sugar for "sudo" command in UNIX / Linux
if platform.system() == "OpenBSD":
    SUDO = ["/usr/bin/doas"]
elif platform.system() == "Windows":
    SUDO = ["powershell", "Start-Process", "powershell", "-Verb", "runAs"]
else:
    SUDO = ["/usr/bin/env", "sudo"]


# Project Settings
BASEDIR_PATH = os.path.dirname(os.path.realpath(__file__))


def get_defaults():
    """
    Helper method for getting the default settings.

    Returns
    -------
    default_settings : dict
        A dictionary of the default settings when updating host information.
    """

    return {
        "numberofrules": 0,
        "datapath": path_join_robust(BASEDIR_PATH, "data"),
        "freshen": True,
        "replace": False,
        "backup": False,
        "skipstatichosts": False,
        "keepdomaincomments": True,
        "extensionspath": path_join_robust(BASEDIR_PATH, "extensions"),
        "extensions": [],
        "nounifiedhosts": False,
        "compress": False,
        "minimise": False,
        "outputsubfolder": "",
        "hostfilename": "hosts",
        "targetips": ["0.0.0.0", "::"],
        "sourcedatafilename": "update.json",
        "sourcesdata": [],
        "readmefilename": "readme.md",
        "readmetemplate": path_join_robust(BASEDIR_PATH, "readme_template.md"),
        "readmedata": {},
        "readmedatafilename": path_join_robust(BASEDIR_PATH, "readmeData.json"),
        "exclusionpattern": r"([a-zA-Z\d-]+\.){0,}",
        "exclusionregexes": [],
        "exclusions": [],
        "commonexclusions": ["hulu.com"],
        "blacklistfile": path_join_robust(BASEDIR_PATH, "blacklist"),
        "whitelistfile": path_join_robust(BASEDIR_PATH, "whitelist"),
        "addsystemhostname": True,
    }


# End Project Settings


def main():
    parser = argparse.ArgumentParser(
        description="Creates a unified hosts "
        "file from hosts stored in the data subfolders."
    )
    parser.add_argument(
        "--auto",
        "-a",
        dest="auto",
        default=False,
        action="store_true",
        help="Run without prompting.",
    )
    parser.add_argument(
        "--backup",
        "-b",
        dest="backup",
        default=False,
        action="store_true",
        help="Backup the hosts files before they are overridden.",
    )
    parser.add_argument(
        "--extensions",
        "-e",
        dest="extensions",
        default=[],
        nargs="*",
        help="Host extensions to include in the final hosts file.",
    )
    parser.add_argument(
        "--nounifiedhosts",
        dest="nounifiedhosts",
        default=False,
        action="store_true",
        help="Do not include the unified hosts file in the final hosts file. Usually used together with `--extensions`.",
    )
    parser.add_argument(
        "--ip",
        "-i",
        dest="targetips",
        nargs="+",
        default=["0.0.0.0", "::"],
        help="""Target IP address(es). Default is ["0.0.0.0", "::"].""",
    )
    parser.add_argument(
        "--keepdomaincomments",
        "-k",
        dest="keepdomaincomments",
        action="store_false",
        default=True,
        help="Do not keep domain line comments.",
    )
    parser.add_argument(
        "--noupdate",
        "-n",
        dest="noupdate",
        default=False,
        action="store_true",
        help="Don't update from host data sources.",
    )
    parser.add_argument(
        "--skipstatichosts",
        "-s",
        dest="skipstatichosts",
        default=False,
        action="store_true",
        help="Skip static localhost entries in the final hosts file.",
    )
    parser.add_argument(
        "--nogendata",
        "-g",
        dest="nogendata",
        default=False,
        action="store_true",
        help="Skip generation of readmeData.json",
    )
    parser.add_argument(
        "--output",
        "-o",
        dest="outputsubfolder",
        default="",
        help="Output subfolder for generated hosts file.",
    )
    parser.add_argument(
        "--replace",
        "-r",
        dest="replace",
        default=False,
        action="store_true",
        help="Replace your active hosts file with this new hosts file.",
    )
    parser.add_argument(
        "--flush-dns-cache",
        "-f",
        dest="flushdnscache",
        default=False,
        action="store_true",
        help="Attempt to flush DNS cache after replacing the hosts file.",
    )
    parser.add_argument(
        "--compress",
        "-c",
        dest="compress",
        default=False,
        action="store_true",
        help="Compress the hosts file ignoring non-necessary lines "
        "(empty lines and comments) and putting multiple domains in "
        "each line. Improve the performance under Windows.",
    )
    parser.add_argument(
        "--minimise",
        "-m",
        dest="minimise",
        default=False,
        action="store_true",
        help="Minimise the hosts file ignoring non-necessary lines "
        "(empty lines and comments).",
    )
    parser.add_argument(
        "--whitelist",
        "-w",
        dest="whitelistfile",
        default=path_join_robust(BASEDIR_PATH, "whitelist"),
        help="Whitelist file to use while generating hosts files.",
    )
    parser.add_argument(
        "--blacklist",
        "-x",
        dest="blacklistfile",
        default=path_join_robust(BASEDIR_PATH, "blacklist"),
        help="Blacklist file to use while generating hosts files.",
    )
    parser.add_argument(
        "--dont-add-system-hostname",
        "-d",
        dest="addsystemhostname",
        default=True,
        action="store_false",
        help="Don't add the current system hostname while generating hosts files.",
    )

    global settings

    options = vars(parser.parse_args())

    options["outputpath"] = path_join_robust(BASEDIR_PATH, options["outputsubfolder"])
    options["freshen"] = not options["noupdate"]

    defaults = get_defaults()
    settings = defaults.copy()
    settings.update(options)

    datapath = settings["datapath"]
    extensionspath = settings["extensionspath"]

    settings["sources"] = list_dir_no_hidden(datapath)
    settings["extensionsources"] = list_dir_no_hidden(extensionspath)

    # All our extensions folders...
    settings["extensions"] = [
        os.path.basename(item) for item in list_dir_no_hidden(extensionspath)
    ]
    # ... intersected with the extensions passed-in as arguments, then sorted.
    settings["extensions"] = sorted(
        list(set(options["extensions"]).intersection(settings["extensions"]))
    )

    auto = settings["auto"]
    exclusionregexes = settings["exclusionregexes"]
    sourcedatafilename = settings["sourcedatafilename"]
    nounifiedhosts = settings["nounifiedhosts"]

    updatesources = prompt_for_update(freshen=settings["freshen"], updateauto=auto)
    if updatesources:
        update_all_sources(sourcedatafilename, settings["hostfilename"])

    gatherexclusions = prompt_for_exclusions(skipprompt=auto)

    if gatherexclusions:
        commonexclusions = settings["commonexclusions"]
        exclusionpattern = settings["exclusionpattern"]
        exclusionregexes = display_exclusion_options(
            commonexclusions=commonexclusions,
            exclusionpattern=exclusionpattern,
            exclusionregexes=exclusionregexes,
        )

    targetips = set(settings["targetips"])
    targetips_updated = targetips != set(defaults["targetips"])
    generatev4, generatev6 = prompt_for_v4_v6(skipprompt=(auto or targetips_updated))
    if not generatev4:
        targetips.remove("0.0.0.0")
    if not generatev6:
        targetips.remove("::")
    print()
    if len(targetips) == 0:
        print_failure("Target IP list is empty!")
        exit(1)

    extensions = settings["extensions"]
    sourcesdata = update_sources_data(
        settings["sourcesdata"],
        datapath=datapath,
        extensions=extensions,
        extensionspath=extensionspath,
        sourcedatafilename=sourcedatafilename,
        nounifiedhosts=nounifiedhosts,
    )

    remove_old_hosts_file(settings["outputpath"], "hosts", settings["backup"])

    if not os.path.exists(settings["outputpath"]):
        os.makedirs(settings["outputpath"])

    finalfile = open(path_join_robust(settings["outputpath"], "hosts"), "w+b")
    with create_initial_file(nounifiedhosts=nounifiedhosts) as mergefile:
        if settings["compress"]:
            with tempfile.NamedTemporaryFile() as uncompressedfile:
                remove_dups_and_excl(mergefile, exclusionregexes, targetips, uncompressedfile)
                compress_file(uncompressedfile, targetips, finalfile)
        elif settings["minimise"]:
            with tempfile.NamedTemporaryFile() as unminimisedfile:
                remove_dups_and_excl(mergefile, exclusionregexes, targetips, unminimisedfile)
                minimise_file(unminimisedfile, targetips, finalfile)
        else:
            remove_dups_and_excl(mergefile, exclusionregexes, targetips, finalfile)

    numberofrules = settings["numberofrules"]
    outputsubfolder = settings["outputsubfolder"]
    skipstatichosts = settings["skipstatichosts"]

    write_opening_header(
        finalfile,
        extensions=extensions,
        numberofrules=numberofrules,
        outputsubfolder=outputsubfolder,
        skipstatichosts=skipstatichosts,
        nounifiedhosts=nounifiedhosts,
        addsystemhostname=settings["addsystemhostname"],
    )
    finalfile.close()

    if not settings["nogendata"]:
        update_readme_data(
            settings["readmedatafilename"],
            extensions=extensions,
            numberofrules=numberofrules,
            outputsubfolder=outputsubfolder,
            sourcesdata=sourcesdata,
            nounifiedhosts=nounifiedhosts,
        )

    print_success(
        "Success! The hosts file has been saved in folder "
        + "./"
        + outputsubfolder
        + "\nIt contains "
        + "{:,}".format(numberofrules)
        + " unique entries."
    )

    movefile = prompt_for_move(
        finalfile,
        auto=auto,
        replace=settings["replace"],
        skipstatichosts=skipstatichosts,
    )

    # We only flush the DNS cache if we have
    # moved a new hosts file into place.
    if movefile:
        prompt_for_flush_dns_cache(
            flushcache=settings["flushdnscache"], promptflush=not auto
        )


# Prompt the User
def prompt_for_update(freshen, updateauto):
    """
    Prompt the user to update all hosts files.

    If requested, the function will update all data sources after it
    checks that a hosts file does indeed exist.

    Parameters
    ----------
    freshen : bool
        Whether data sources should be updated. This function will return
        if it is requested that data sources not be updated.
    updateauto : bool
        Whether or not to automatically update all data sources.

    Returns
    -------
    updatesources : bool
        Whether or not we should update data sources for exclusion files.
    """

    # Create a hosts file if it doesn't exist.
    hostsfile = path_join_robust(BASEDIR_PATH, "hosts")

    if not os.path.isfile(hostsfile):
        try:
            open(hostsfile, "w+").close()
        except (IOError, OSError):
            # Starting in Python 3.3, IOError is aliased
            # OSError. However, we have to catch both for
            # Python 2.x failures.
            print_failure(
                "ERROR: No 'hosts' file in the folder. Try creating one manually."
            )

    if not freshen:
        return False

    prompt = "Do you want to update all data sources?"

    if updateauto or query_yes_no(prompt):
        return True
    elif not updateauto:
        print("OK, we'll stick with what we've got locally.")

    return False


def prompt_for_exclusions(skipprompt):
    """
    Prompt the user to exclude any custom domains from being blocked.

    Parameters
    ----------
    skipprompt : bool
        Whether or not to skip prompting for custom domains to be excluded.
        If true, the function returns immediately.

    Returns
    -------
    gatherexclusions : bool
        Whether or not we should proceed to prompt the user to exclude any
        custom domains beyond those in the whitelist.
    """

    prompt = (
        "Do you want to exclude any domains?\n"
        "For example, hulu.com video streaming must be able to access "
        "its tracking and ad servers in order to play video."
    )

    if not skipprompt:
        if query_yes_no(prompt):
            return True
        else:
            print("OK, we'll only exclude domains in the whitelist.")

    return False


def prompt_for_v4_v6(skipprompt):
    """
    Prompt the user to add v4 or v6 rules.

    Parameters
    ----------
    skipprompt : bool
        Whether or not to skip prompting.
        If true, the function returns immediately.

    Returns
    -------
    generatev4 : bool
        Whether or not we should generate v4 rules.
    generatev6 : bool
        Whether or not we should generate v6 rules.
    """

    prompt_unformatted = (
        "Do you want to add {} rules?\n"
        "This roughly doubles the file size, but may be "
        "necessary to actually block hosts\n"
        "depending on your network configuration."
    )
    prompt_v4 = prompt_unformatted.format("IPv4")
    prompt_v6 = prompt_unformatted.format("IPv6")

    generatev4 = True
    generatev6 = True

    if not skipprompt:
        if not query_yes_no(prompt_v4):
            print("OK, we'll skip adding v4 rules.")
            generatev4 = False
        if not query_yes_no(prompt_v6):
            print("OK, we'll skip adding v6 rules.")
            generatev6 = False

    return generatev4, generatev6


def prompt_for_flush_dns_cache(flushcache, promptflush):
    """
    Prompt the user to flush the DNS cache.

    Parameters
    ----------
    flushcache : bool
        Whether to flush the DNS cache without prompting.
    promptflush : bool
        If `flushcache` is False, whether we should prompt for flushing the
        cache. Otherwise, the function returns immediately.
    """

    if flushcache:
        flush_dns_cache()
    elif promptflush:
        if query_yes_no("Attempt to flush the DNS cache?"):
            flush_dns_cache()


def prompt_for_move(finalfile, **moveparams):
    """
    Prompt the user to move the newly created hosts file to its designated
    location in the OS.

    Parameters
    ----------
    finalfile : file
        The file object that contains the newly created hosts data.
    moveparams : kwargs
        Dictionary providing additional parameters for moving the hosts file
        into place. Currently, those fields are:

        1) auto
        2) replace
        3) skipstatichosts

    Returns
    -------
    movefile : bool
        Whether or not the final hosts file was moved.
    """

    skipstatichosts = moveparams["skipstatichosts"]

    if moveparams["replace"] and not skipstatichosts:
        movefile = True
    elif moveparams["auto"] or skipstatichosts:
        movefile = False
    else:
        prompt = "Do you want to replace your existing hosts file with the newly generated file?"
        movefile = query_yes_no(prompt)

    if movefile:
        movefile = move_hosts_file_into_place(finalfile)

    return movefile


# End Prompt the User


def sort_sources(sources):
    """
    Sorts the sources.
    The idea is that all Steven Black's list, file or entries
    get on top and the rest sorted alphabetically.

    Parameters
    ----------
    sources: list
        The sources to sort.
    """

    result = sorted(
        sources.copy(),
        key=lambda x: x.lower().replace("-", "").replace("_", "").replace(" ", ""),
    )

    # Steven Black's repositories/files/lists should be on top!
    stevenblackpositions = [
        x for x, y in enumerate(result) if "stevenblack" in y.lower()
    ]

    for index in stevenblackpositions:
        result.insert(0, result.pop(index))

    return result


# Exclusion logic
def display_exclusion_options(commonexclusions, exclusionpattern, exclusionregexes):
    """
    Display the exclusion options to the user.

    This function checks whether a user wants to exclude particular domains,
    and if so, excludes them.

    Parameters
    ----------
    commonexclusions : list
        A list of common domains that are excluded from being blocked. One
        example is Hulu. This setting is set directly in the script and cannot
        be overwritten by the user.
    exclusionpattern : str
        The exclusion pattern with which to create the domain regex.
    exclusionregexes : list
        The list of regex patterns used to exclude domains.

    Returns
    -------
    aug_exclusionregexes : list
        The original list of regex patterns potentially with additional
        patterns from domains that the user chooses to exclude.
    """

    for exclusionoption in commonexclusions:
        prompt = "Do you want to exclude the domain " + exclusionoption + " ?"

        if query_yes_no(prompt):
            exclusionregexes = exclude_domain(
                exclusionoption, exclusionpattern, exclusionregexes
            )
        else:
            continue

    if query_yes_no("Do you want to exclude any other domains?"):
        exclusionregexes = gather_custom_exclusions(
            exclusionpattern, exclusionregexes
        )

    return exclusionregexes


def gather_custom_exclusions(exclusionpattern, exclusionregexes):
    """
    Gather custom exclusions from the user.

    Parameters
    ----------
    exclusionpattern : str
        The exclusion pattern with which to create the domain regex.
    exclusionregexes : list
        The list of regex patterns used to exclude domains.

    Returns
    -------
    aug_exclusionregexes : list
        The original list of regex patterns potentially with additional
        patterns from domains that the user chooses to exclude.
    """

    # We continue running this while-loop until the user
    # says that they have no more domains to exclude.
    while True:
        domainprompt = "Enter the domain you want to exclude (e.g. facebook.com): "
        userdomain = input(domainprompt)

        if is_valid_user_provided_domain_format(userdomain):
            exclusionregexes = exclude_domain(
                userdomain, exclusionpattern, exclusionregexes
            )

        continueprompt = "Do you have more domains you want to enter?"
        if not query_yes_no(continueprompt):
            break

    return exclusionregexes


def exclude_domain(domain, exclusionpattern, exclusionregexes):
    """
    Exclude a domain from being blocked.

    This creates the domain regex by which to exclude this domain and appends
    it a list of already-existing exclusion regexes.

    Parameters
    ----------
    domain : str
        The filename or regex pattern to exclude.
    exclusionpattern : str
        The exclusion pattern with which to create the domain regex.
    exclusionregexes : list
        The list of regex patterns used to exclude domains.

    Returns
    -------
    aug_exclusionregexes : list
        The original list of regex patterns with one additional pattern from
        the `domain` input.
    """

    exclusionregex = re.compile(exclusionpattern + domain)
    exclusionregexes.append(exclusionregex)

    return exclusionregexes


def matches_exclusions(strippedrule, exclusionregexes):
    """
    Check whether a rule matches an exclusion rule we already provided.

    If this function returns True, that means this rule should be excluded
    from the final hosts file.

    Parameters
    ----------
    strippedrule : str
        The rule that we are checking.
    exclusionregexes : list
        The list of regex patterns used to exclude domains.

    Returns
    -------
    matches_exclusion : bool
        Whether or not the rule string matches a provided exclusion.
    """

    try:
        strippeddpmain = strippedrule.split()[1]
    except IndexError:
        # Example: 'example.org' instead of '0.0.0.0 example.org'
        strippeddpmain = strippedrule

    for exclusionRegex in exclusionregexes:
        if exclusionRegex.search(strippeddpmain):
            return True

    return False


# End Exclusion Logic


# Update Logic
def update_sources_data(sourcesdata, **sourcesparams):
    """
    Update the sources data and information for each source.

    Parameters
    ----------
    sourcesdata : list
        The list of sources data that we are to update.
    sourcesparams : kwargs
        Dictionary providing additional parameters for updating the
        sources data. Currently, those fields are:

        1) datapath
        2) extensions
        3) extensionspath
        4) sourcedatafilename
        5) nounifiedhosts

    Returns
    -------
    update_sources_data : list
        The original source data list with new source data appended.
    """

    sourcedatafilename = sourcesparams["sourcedatafilename"]

    if not sourcesparams["nounifiedhosts"]:
        for source in sort_sources(
            recursive_glob(sourcesparams["datapath"], sourcedatafilename)
        ):
            updatefile = open(source, "r", encoding="UTF-8")
            try:
                updatedata = json.load(updatefile)
                sourcesdata.append(updatedata)
            finally:
                updatefile.close()

    for source in sourcesparams["extensions"]:
        sourcedir = path_join_robust(sourcesparams["extensionspath"], source)
        for updatefile_path in sort_sources(
            recursive_glob(sourcedir, sourcedatafilename)
        ):
            updatefile = open(updatefile_path, "r")
            try:
                updatedata = json.load(updatefile)
                sourcesdata.append(updatedata)
            finally:
                updatefile.close()

    return sourcesdata


def jsonarray(json_array_string):
    """
    Transformer, converts a json array string hosts into one host per
    line, prefixing each line with "127.0.0.1 ".

    Parameters
    ----------
    json_array_string : str
        The json array string in the form
          '["example1.com", "example1.com", ...]'
    """

    templist = json.loads(json_array_string)
    hostlines = "127.0.0.1 " + "\n127.0.0.1 ".join(templist)
    return hostlines


def update_all_sources(sourcedatafilename, hostfilename):
    """
    Update all host files, regardless of folder depth.

    Parameters
    ----------
    sourcedatafilename : str
        The name of the filename where information regarding updating
        sources for a particular URL is stored. This filename is assumed
        to be the same for all sources.
    hostfilename : str
        The name of the file in which the updated source information
        is stored for a particular URL. This filename is assumed to be
        the same for all sources.
    """

    # The transforms we support
    transformmethods = {"jsonarray": jsonarray}

    allsources = sort_sources(recursive_glob("*", sourcedatafilename))

    for source in allsources:
        updatefile = open(source, "r", encoding="UTF-8")
        updatedata = json.load(updatefile)
        updatefile.close()

        # we can pause updating any given hosts source.
        # if the update.json "pause" key is missing, don't pause.
        if updatedata.get("pause", False):
            continue

        updateurl = updatedata["url"]
        update_transforms = []
        if updatedata.get("transforms"):
            update_transforms = updatedata["transforms"]

        print("Updating source " + os.path.dirname(source) + " from " + updateurl)

        try:
            updatedfile = get_file_by_url(updateurl)

            # spin the transforms as required
            for transform in update_transforms:
                updatedfile = transformmethods[transform](updatedfile)

            # get rid of carriage-return symbols
            updatedfile = updatedfile.replace("\r", "")

            hostsfile = open(
                path_join_robust(BASEDIR_PATH, os.path.dirname(source), hostfilename),
                "wb",
            )
            write_data(hostsfile, updatedfile)
            hostsfile.close()
        except Exception:
            print("Error in updating source: ", updateurl)


# End Update Logic


# File Logic
def create_initial_file(**initial_file_params):
    """
    Initialize the file in which we merge all host files for later pruning.

    Parameters
    ----------
    headerparams : kwargs
        Dictionary providing additional parameters for populating the initial file
        information. Currently, those fields are:

        1) nounifiedhosts
    """

    mergefile = tempfile.NamedTemporaryFile()

    if not initial_file_params["nounifiedhosts"]:
        # spin the sources for the base file
        for source in sort_sources(
            recursive_glob(settings["datapath"], settings["hostfilename"])
        ):
            start = "# Start {}\n\n".format(os.path.basename(os.path.dirname(source)))
            end = "\n# End {}\n\n".format(os.path.basename(os.path.dirname(source)))

            with open(source, "r", encoding="UTF-8") as curFile:
                write_data(mergefile, start + curFile.read() + end)

    # spin the sources for extensions to the base file
    for source in settings["extensions"]:
        for filename in sort_sources(
            recursive_glob(
                path_join_robust(settings["extensionspath"], source),
                settings["hostfilename"],
            )
        ):
            with open(filename, "r") as curFile:
                write_data(mergefile, curFile.read())

    maybe_copy_example_file(settings["blacklistfile"])

    if os.path.isfile(settings["blacklistfile"]):
        with open(settings["blacklistfile"], "r") as curFile:
            write_data(mergefile, curFile.read())

    return mergefile


def compress_file(inputfile, targetips, outputfile, maxdomainsperline=9):
    """
    Reduce the file dimension removing non-necessary lines (empty lines and
    comments) and putting multiple domains in each line.
    Reducing the number of lines of the file, the parsing under Microsoft
    Windows is much faster.

    Parameters
    ----------
    inputfile : file
        The file object that contains the hostnames that we are reducing.
    targetips : list[str]
        The target IP address.
    outputfile : file
        The file object that will contain the reduced hostnames.
    maxdomainsperline : int
        The maximum number of domains per line. Defaults to 9.
    """

    inputfile.seek(0)  # reset file pointer
    write_data(outputfile, "\n")

    ip_lines = {ip: [] for ip in targetips}

    for line in inputfile.readlines():
        line = line.decode("UTF-8").strip()

        if not line or line.startswith("#"):
            continue

        for targetip in targetips:
            if line.startswith(targetip):
                domain_part = line[len(targetip) : line.find("#")].strip() if "#" in line else line[len[targetip] :].strip()

                if len(ip_lines[targetip]) == 0 or ip_lines[targetip][-1].count(" ") >= maxdomainsperline:
                    ip_lines[targetip].append(targetip + " " + domain_part)
                else:
                    ip_lines[targetip][-1] += " " + domain_part
                break

    for targetip in targetips:
        for line in ip_lines[targetip]:
            write_data(outputfile, line + "\n")

    inputfile.close()


def minimise_file(inputfile, targetips, outputfile):
    """
    Reduce the file dimension removing non-necessary lines (empty lines and
    comments).

    Parameters
    ----------
    inputfile : file
        The file object that contains the hostnames that we are reducing.
    targetips : list[str]
        The target IP addresses.
    outputfile : file
        The file object that will contain the reduced hostnames.
    """

    inputfile.seek(0)  # reset file pointer
    write_data(outputfile, "\n")

    lines = []
    for line in inputfile.readlines():
        line = line.decode("UTF-8")

        for targetip in targetips:
            if line.startswith(targetip):
                lines.append(line[: line.find("#")].strip() + "\n")

    for line in lines:
        write_data(outputfile, line)

    inputfile.close()


def remove_dups_and_excl(mergefile, exclusionregexes, targetips, outputfile):
    """
    Remove duplicates and remove hosts that we are excluding.

    We check for duplicate hostnames as well as remove any hostnames that
    have been explicitly excluded by the user.

    Parameters
    ----------
    mergefile : file
        The file object that contains the hostnames that we are pruning.
    exclusionregexes : list
        The list of regex patterns used to exclude domains.
    targetips : list[str]
        The list of target IP addresses
    outputfile : file
        The file object to which the result is written.
    """

    numberofrules = settings["numberofrules"]
    maybe_copy_example_file(settings["whitelistfile"])

    if os.path.isfile(settings["whitelistfile"]):
        with open(settings["whitelistfile"], "r") as ins:
            for line in ins:
                line = line.strip(" \t\n\r")
                if line and not line.startswith("#"):
                    settings["exclusions"].append(line)

    finalfile = outputfile

    # analyze any post.json here
    post_json_path = os.path.join(os.path.dirname(finalfile.name), "post.json")
    filters = []
    if os.path.isfile(post_json_path):
        try:
            with open(post_json_path, "r", encoding="UTF-8") as post_file:
                post_data = json.load(post_file)
                filters = post_data.get("filters", [])
        except Exception as e:
            print_failure(f"Error reading post.json: {e}")

    mergefile.seek(0)  # reset file pointer
    hostnames = {"localhost", "localhost.localdomain", "local", "broadcasthost"}
    exclusions = settings["exclusions"]

    for line in mergefile.readlines():
        write_line = True

        # Explicit encoding
        line = line.decode("UTF-8")

        # Apply post.json filters
        if filters and any(f in line for f in filters):
            continue

        # replace tabs with space
        line = line.replace("\t+", " ")

        # see gh-271: trim trailing whitespace, periods
        line = line.rstrip(" .")

        # Testing the first character doesn't require startswith
        if line[0] == "#" or re.match(r"^\s*$", line[0]):
            write_data(finalfile, line)
            continue
        if "::1" in line:
            continue

        strippedrule = strip_rule(line)  # strip comments
        if not strippedrule or matches_exclusions(strippedrule, exclusionregexes):
            continue

        # Issue #1628
        if "@" in strippedrule:
            continue

        for exclude in exclusions:
            if re.search(r"(^|[\s\.])" + re.escape(exclude) + r"\s", line):
                write_line = False
                break

        # Normalize rule
        hostname, has_rule = normalize_rule(
            strippedrule,
            targetip="0.0.0.0",
            keep_domain_comments=settings["keepdomaincomments"],
        )
        if write_line and (hostname not in hostnames) and has_rule:
            hostnames.add(hostname)
            numberofrules += 1
            for targetip in targetips:
                _, normalized_rule = normalize_rule(
                    strippedrule,
                    targetip=targetip,
                    keep_domain_comments=settings["keepdomaincomments"],
                )
                write_data(finalfile, normalized_rule)

    settings["numberofrules"] = numberofrules


def normalize_rule(rule, targetip, keep_domain_comments):
    """
    Standardize and format the rule string provided.

    Parameters
    ----------
    rule : str
        The rule whose spelling and spacing we are standardizing.
    targetip : str
        The target IP address for the rule.
    keep_domain_comments : bool
        Whether or not to keep comments regarding these domains in
        the normalized rule.

    Returns
    -------
    normalized_rule : tuple
        A tuple of the hostname and the rule string with spelling
        and spacing reformatted.
    """

    def normalize_response(
        extracted_hostname: str, extracted_suffix: Optional[str]
    ) -> Tuple[str, str]:
        """
        Normalizes the responses after the provision of the extracted
        hostname and suffix - if exist.

        Parameters
        ----------
        extracted_hostname: str
            The extracted hostname to work with.
        extracted_suffix: str
            The extracted suffix to with.

        Returns
        -------
        normalized_response: tuple
            A tuple of the hostname and the rule string with spelling
            and spacing reformatted.
        """

        hostname = extracted_hostname.lower()

        rule = "%s %s" % (targetip, hostname)

        if keep_domain_comments and extracted_suffix:
            if not extracted_suffix.strip().startswith("#"):
                # Strings are stripped, therefore we need to add the space back.
                rule += " # %s" % extracted_suffix
            else:
                rule += " %s" % extracted_suffix

        return hostname, rule + "\n"

    def is_ip(dataset: str) -> bool:
        """
        Checks whether the given dataset is an IP.

        Parameters
        ----------

        dataset: str
            The dataset to work with.

        Returns
        -------
        is_ip: bool
            Whether the dataset is an IP.
        """

        try:
            _ = ipaddress.ip_address(dataset)
            return True
        except ValueError:
            return False

    def is_valid_hostname(dataset: str, min_labels: int = 1) -> bool:
        """
        Validates a hostname according to RFC 1123 Section 2.5.

        - Hostname must be <= 255 characters.
        - Each label (dot-separated part) must be <= 63 characters.
        - Labels may contain letters, digits, and hyphens.
        - Labels must not start or end with a hyphen (but may start with a digit!).

        Parameters
        ----------

        dataset : str
            The dataset to validate
        min_labels : int
            The minimum number of labels to require.

        Returns
        ------
        is_valid_hostname: bool
            Whether the dataset is a hostname
        """
        if len(dataset) > 255:
            return False
        if dataset.endswith("."):
            dataset = dataset[:-1]

        label_regex = re.compile(r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)$")
        labels = dataset.split(".")
        return all(label_regex.match(label) for label in labels) and len(labels) >= min_labels

    def belch_unwanted(unwanted: str) -> Tuple[None, None]:
        """
        Belches unwanted to screen.

        Parameters
        ----------
        unwanted: str
            The unwanted string to belch.

        Returns
        -------
        belched: tuple
            A tuple of None, None.
        """

        """
        finally, if we get here, just belch to screen
        """
        print("==>%s<==" % unwanted)
        return None, None

    """
    first try: IP followed by domain
    """

    split_rule = rule.split(maxsplit=1)

    if is_ip(split_rule[0]):
        # Assume that the first item is an IP address, discard as we're replacing it with targetip

        split_rule = split_rule[-1].split(maxsplit=1)

    if is_valid_hostname(split_rule[0]):
        # Assume that the next item is the hostname

        hostname = split_rule[0]
        suffix = split_rule[1] if len(split_rule) > 1 else None
    else:
        return belch_unwanted(rule)

    # If the hostname is invalid or looks like an IP, we don't want to normalize it.
    # If we were wanting 100% compliance with the RFC we'd use min_labels=1,
    # but we want to stop TLDs from being blocked so we set this to 2.
    if not is_valid_hostname(hostname, 2) or is_ip(hostname):
        return belch_unwanted(rule)

    return normalize_response(hostname, suffix)


def strip_rule(line):
    """
    Sanitize a rule string provided before writing it to the output hosts file.

    Parameters
    ----------
    line : str
        The rule provided for sanitation.

    Returns
    -------
    sanitized_line : str
        The sanitized rule.
    """

    return " ".join(line.split())


def write_opening_header(finalfile, **headerparams):
    """
    Write the header information into the newly-created hosts file.

    Parameters
    ----------
    finalfile : file
        The file object that points to the newly-created hosts file.
    headerparams : kwargs
        Dictionary providing additional parameters for populating the header
        information. Currently, those fields are:

        1) extensions
        2) numberofrules
        3) outputsubfolder
        4) skipstatichosts
        5) nounifiedhosts
        6) hostfilename
    """

    finalfile.seek(0)  # Reset file pointer.
    file_contents = finalfile.read()  # Save content.

    finalfile.seek(0)  # Write at the top.

    nounifiedhosts = headerparams["nounifiedhosts"]

    if headerparams["extensions"]:
        if nounifiedhosts:
            if len(headerparams["extensions"]) > 1:
                write_data(
                    finalfile,
                    "# Title: StevenBlack/hosts extensions {0} and {1} \n#\n".format(
                        ", ".join(headerparams["extensions"][:-1]),
                        headerparams["extensions"][-1],
                    ),
                )
            else:
                write_data(
                    finalfile,
                    "# Title: StevenBlack/hosts extension {0}\n#\n".format(
                        ", ".join(headerparams["extensions"])
                    ),
                )
        else:
            if len(headerparams["extensions"]) > 1:
                write_data(
                    finalfile,
                    "# Title: StevenBlack/hosts with the {0} and {1} extensions\n#\n".format(
                        ", ".join(headerparams["extensions"][:-1]),
                        headerparams["extensions"][-1],
                    ),
                )
            else:
                write_data(
                    finalfile,
                    "# Title: StevenBlack/hosts with the {0} extension\n#\n".format(
                        ", ".join(headerparams["extensions"])
                    ),
                )
    else:
        write_data(finalfile, "# Title: StevenBlack/hosts\n#\n")

    write_data(
        finalfile,
        "# This hosts file is a merged collection "
        "of hosts from reputable sources,\n",
    )
    write_data(finalfile, "# with a dash of crowd sourcing via GitHub\n#\n")
    write_data(
        finalfile,
        "# Date: " + time.strftime("%d %B %Y %H:%M:%S (%Z)", time.gmtime()) + "\n",
    )

    if headerparams["extensions"]:
        if headerparams["nounifiedhosts"]:
            write_data(
                finalfile,
                "# The unified hosts file was not used while generating this file.\n"
                "# Extensions used to generate this file: "
                + ", ".join(headerparams["extensions"])
                + "\n",
            )
        else:
            write_data(
                finalfile,
                "# Extensions added to this file: "
                + ", ".join(headerparams["extensions"])
                + "\n",
            )

    write_data(
        finalfile,
        (
            "# Number of unique domains: {:,}\n#\n".format(
                headerparams["numberofrules"]
            )
        ),
    )
    write_data(
        finalfile,
        "# Fetch the latest version of this file: "
        "https://raw.githubusercontent.com/StevenBlack/hosts/master/"
        + path_join_robust(headerparams["outputsubfolder"], "").replace("\\", "/")
        + "hosts\n",
    )
    write_data(
        finalfile, "# Project home page: https://github.com/StevenBlack/hosts\n"
    )
    write_data(
        finalfile,
        "# Project releases: https://github.com/StevenBlack/hosts/releases\n#\n",
    )
    write_data(
        finalfile,
        "# ===============================================================\n",
    )
    write_data(finalfile, "\n")

    if not headerparams["skipstatichosts"]:
        write_data(finalfile, "127.0.0.1 localhost\n")
        write_data(finalfile, "127.0.0.1 localhost.localdomain\n")
        write_data(finalfile, "127.0.0.1 local\n")
        write_data(finalfile, "255.255.255.255 broadcasthost\n")
        write_data(finalfile, "::1 localhost\n")
        write_data(finalfile, "::1 ip6-localhost\n")
        write_data(finalfile, "::1 ip6-loopback\n")
        write_data(finalfile, "fe80::1%lo0 localhost\n")
        write_data(finalfile, "ff00::0 ip6-localnet\n")
        write_data(finalfile, "ff00::0 ip6-mcastprefix\n")
        write_data(finalfile, "ff02::1 ip6-allnodes\n")
        write_data(finalfile, "ff02::2 ip6-allrouters\n")
        write_data(finalfile, "ff02::3 ip6-allhosts\n")
        write_data(finalfile, "0.0.0.0 0.0.0.0\n")

        if platform.system() == "Linux" and "addsystemhostname" in headerparams.keys() and headerparams["addsystemhostname"]:
            write_data(finalfile, "127.0.1.1 " + socket.gethostname() + "\n")
            write_data(finalfile, "127.0.0.53 " + socket.gethostname() + "\n")

        write_data(finalfile, "\n")

    preamble = path_join_robust(BASEDIR_PATH, "myhosts")
    maybe_copy_example_file(preamble)

    if os.path.isfile(preamble):
        with open(preamble, "r") as f:
            write_data(finalfile, f.read())

    finalfile.write(file_contents)


def update_readme_data(readme_file, **readme_updates):
    """
    Update the host and website information provided in the README JSON data.

    Parameters
    ----------
    readme_file : str
        The name of the README file to update.
    readme_updates : kwargs
        Dictionary providing additional JSON fields to update before
        saving the data. Currently, those fields are:

        1) extensions
        2) sourcesdata
        3) numberofrules
        4) outputsubfolder
        5) nounifiedhosts
    """

    extensions_key = "base"
    extensions = readme_updates["extensions"]
    nounifiedhosts = readme_updates["nounifiedhosts"]

    if extensions:
        extensions_key = "-".join(extensions)
        if nounifiedhosts:
            extensions_key = extensions_key + "-only"

    output_folder = readme_updates["outputsubfolder"]
    generation_data = {
        "location": path_join_robust(output_folder, ""),
        "nounifiedhosts": nounifiedhosts,
        "entries": readme_updates["numberofrules"],
        "sourcesdata": readme_updates["sourcesdata"],
    }

    with open(readme_file, "r") as f:
        readme_data = json.load(f)
        readme_data[extensions_key] = generation_data

    for denomination, data in readme_data.copy().items():
        if "location" in data and data["location"] and "\\" in data["location"]:
            # Windows compatibility: #1166
            readme_data[denomination]["location"] = data["location"].replace("\\", "/")

    with open(readme_file, "w") as f:
        json.dump(readme_data, f)


def move_hosts_file_into_place(finalfile):
    r"""
    Move the newly-created hosts file into its correct location on the OS.

    For UNIX systems, the hosts file is "etc/hosts." On Windows, it's
    "C:\Windows\System32\drivers\etc\hosts."

    For this move to work, you must have administrator privileges to do this.
    On UNIX systems, this means having "sudo" access, and on Windows, it
    means being able to run command prompt in administrator mode.

    Parameters
    ----------
    finalfile : file object
        The newly-created hosts file to move.
    """  # noqa: W605

    filename = os.path.abspath(finalfile.name)

    try:
        if not Path(filename).exists():
            raise FileNotFoundError
    except Exception:
        print_failure(f"{filename} does not exist.")
        return False

    if platform.system() == "Windows":
        target_file = str(
            Path(os.getenv("SystemRoot")) / "system32" / "drivers" / "etc" / "hosts"
        )
    else:
        target_file = "/etc/hosts"

    if os.getenv("IN_CONTAINER"):
        # It's not allowed to remove/replace a mounted /etc/hosts, so we replace the content.
        # This requires running the container user as root, as is the default.
        print(f"Running in container, so we will replace the content of {target_file}.")
        try:
            with open(target_file, "w") as target_stream:
                with open(filename, "r") as source_stream:
                    source = source_stream.read()
                    target_stream.write(source)
            return True
        except Exception:
            print_failure(f"Replacing content of {target_file} failed.")
            return False
    elif (
        platform.system() == "Linux"
        or platform.system() == "Windows"
        or platform.system() == "Darwin"
    ):
        print(
            f"Replacing {target_file} requires root privileges. You might need to enter your password."
        )
        try:
            subprocess.run(SUDO + ["cp", filename, target_file], check=True)
            return True
        except subprocess.CalledProcessError:
            print_failure(f"Replacing {target_file} failed.")
            return False


def flush_dns_cache():
    """
    Flush the DNS cache.
    """

    print("Flushing the DNS cache to utilize new hosts file...")
    print(
        "Flushing the DNS cache requires administrative privileges. You might need to enter your password."
    )

    dns_cache_found = False

    if platform.system() == "Darwin":
        if subprocess.call(SUDO + ["killall", "-HUP", "mDNSResponder"]):
            print_failure("Flushing the DNS cache failed.")
    elif os.name == "nt":
        print("Automatically flushing the DNS cache is not yet supported.")
        print(
            "Please copy and paste the command 'ipconfig /flushdns' in "
            "administrator command prompt after running this script."
        )
    else:
        nscd_prefixes = ["/etc", "/etc/rc.d"]
        nscd_msg = "Flushing the DNS cache by restarting nscd {result}"

        for nscd_prefix in nscd_prefixes:
            nscd_cache = nscd_prefix + "/init.d/nscd"

            if os.path.isfile(nscd_cache):
                dns_cache_found = True

                if subprocess.call(SUDO + [nscd_cache, "restart"]):
                    print_failure(nscd_msg.format(result="failed"))
                else:
                    print_success(nscd_msg.format(result="succeeded"))

        centos_file = "/etc/init.d/network"
        centos_msg = "Flushing the DNS cache by restarting network {result}"

        if os.path.isfile(centos_file):
            if subprocess.call(SUDO + [centos_file, "restart"]):
                print_failure(centos_msg.format(result="failed"))
            else:
                print_success(centos_msg.format(result="succeeded"))

        system_prefixes = ["/usr", ""]
        service_types = ["NetworkManager", "wicd", "dnsmasq", "networking"]
        restarted_services = []

        for system_prefix in system_prefixes:
            systemctl = system_prefix + "/bin/systemctl"
            system_dir = system_prefix + "/lib/systemd/system"

            for service_type in service_types:
                service = service_type + ".service"
                if service in restarted_services:
                    continue

                service_file = path_join_robust(system_dir, service)
                service_msg = (
                    "Flushing the DNS cache by restarting " + service + " {result}"
                )

                if os.path.isfile(service_file):
                    if 0 != subprocess.call(
                        [systemctl, "status", service], stdout=subprocess.DEVNULL
                    ):
                        continue
                    dns_cache_found = True

                    if subprocess.call(SUDO + [systemctl, "restart", service]):
                        print_failure(service_msg.format(result="failed"))
                    else:
                        print_success(service_msg.format(result="succeeded"))
                    restarted_services.append(service)

        dns_clean_file = "/etc/init.d/dns-clean"
        dns_clean_msg = "Flushing the DNS cache via dns-clean executable {result}"

        if os.path.isfile(dns_clean_file):
            dns_cache_found = True

            if subprocess.call(SUDO + [dns_clean_file, "start"]):
                print_failure(dns_clean_msg.format(result="failed"))
            else:
                print_success(dns_clean_msg.format(result="succeeded"))

        if not dns_cache_found:
            print_failure("Unable to determine DNS management tool.")


def remove_old_hosts_file(path_to_file, file_name, backup):
    """
    Remove the old hosts file.

    This is a hotfix because merging with an already existing hosts file leads
    to artifacts and duplicates.

    Parameters
    ----------
    backup : boolean, default False
        Whether or not to backup the existing hosts file.
    """

    fullfilepath = path_join_robust(path_to_file, file_name)

    if os.path.exists(fullfilepath):
        if backup:
            backupfilepath = fullfilepath + "-{}".format(
                time.strftime("%Y-%m-%d-%H-%M-%S")
            )

            # Make a backup copy, marking the date in which the list was updated
            shutil.copy(fullfilepath, backupfilepath)

        os.remove(fullfilepath)

    # Create directory if not exists
    if not os.path.exists(path_to_file):
        os.makedirs(path_to_file)

    # Create new empty hosts file
    open(fullfilepath, "a").close()


# End File Logic


def domain_to_idna(line):
    """
    Encode a domain that is present into a line into `idna`. This way we
    avoid most encoding issues.

    Parameters
    ----------
    line : str
        The line we have to encode/decode.

    Returns
    -------
    line : str
        The line in a converted format.

    Notes
    -----
    - This function encodes only the domain to `idna` format because in
        most cases, the encoding issue is due to a domain which looks like
        `b'\xc9\xa2oogle.com'.decode('idna')`.
    - About the splitting:
        We split because we only want to encode the domain and not the full
        line, which may cause some issues. Keep in mind that we split, but we
        still concatenate once we encoded the domain.

        - The following split the prefix `0.0.0.0` or `127.0.0.1` of a line.
        - The following also split the trailing comment of a given line.
    """

    if not line.startswith("#"):
        tabs = "\t"
        space = " "

        tabsposition, spaceposition = (line.find(tabs), line.find(space))

        if tabsposition > -1 and spaceposition > -1:
            if spaceposition < tabsposition:
                separator = space
            else:
                separator = tabs
        elif not tabsposition == -1:
            separator = tabs
        elif not spaceposition == -1:
            separator = space
        else:
            separator = ""

        if separator:
            splited_line = line.split(separator)

            try:
                index = 1
                while index < len(splited_line):
                    if splited_line[index]:
                        break
                    index += 1

                if "#" in splited_line[index]:
                    index_comment = splited_line[index].find("#")

                    if index_comment > -1:
                        comment = splited_line[index][index_comment:]

                        splited_line[index] = (
                            splited_line[index]
                            .split(comment)[0]
                            .encode("IDNA")
                            .decode("UTF-8")
                            + comment
                        )

                splited_line[index] = splited_line[index].encode("IDNA").decode("UTF-8")
            except IndexError:
                pass
            return separator.join(splited_line)
        return line.encode("IDNA").decode("UTF-8")
    return line.encode("UTF-8").decode("UTF-8")


# Helper Functions
def maybe_copy_example_file(file_path):
    """
    Given a file path, copy over its ".example" if the path doesn't exist.

    If the path does exist, nothing happens in this function.

    If the path doesn't exist, and the ".example" file doesn't exist, nothing happens in this function.

    Parameters
    ----------
    file_path : str
        The full file path to check.
    """

    if not os.path.isfile(file_path):
        examplefilepath = file_path + ".example"
        if os.path.isfile(examplefilepath):
            shutil.copyfile(examplefilepath, file_path)


def get_file_by_url(url, params=None, **kwargs):
    """
    Retrieve the contents of the hosts file at the URL, then pass it through domain_to_idna().

    Parameters are passed to the requests.get() function.

    Parameters
    ----------
    url : str or bytes
        URL for the new Request object.
    params :
        Dictionary, list of tuples or bytes to send in the query string for the Request.
    kwargs :
        Optional arguments that request takes.

    Returns
    -------
    url_data : str or None
        The data retrieved at that URL from the file. Returns None if the
        attempted retrieval is unsuccessful.
    """

    try:
        req = requests.get(url=url, params=params, **kwargs)
    except requests.exceptions.RequestException:
        print("Error retrieving data from {}".format(url))
        return None

    req.encoding = req.apparent_encoding
    res_text = "\n".join([domain_to_idna(line) for line in req.text.split("\n")])
    return res_text


def write_data(f, data):
    """
    Write data to a file object.

    Parameters
    ----------
    f : file
        The file object at which to write the data.
    data : str
        The data to write to the file.
    """

    f.write(bytes(data, "UTF-8"))


def list_dir_no_hidden(path):
    """
    List all files in a directory, except for hidden files.

    Parameters
    ----------
    path : str
        The path of the directory whose files we wish to list.
    """

    return glob(os.path.join(path, "*"))


def query_yes_no(question, default="yes"):
    """
    Ask a yes/no question via input() and get answer from the user.

    Inspired by the following implementation:

    https://code.activestate.com/recipes/577058/

    Parameters
    ----------
    question : str
        The question presented to the user.
    default : str, default "yes"
        The presumed answer if the user just hits <Enter>. It must be "yes",
        "no", or None (means an answer is required of the user).

    Returns
    -------
    yes : Whether or not the user replied yes to the question.
    """

    valid = {"yes": "yes", "y": "yes", "ye": "yes", "no": "no", "n": "no"}
    prompt = {None: " [y/n] ", "yes": " [Y/n] ", "no": " [y/N] "}.get(default, None)

    if not prompt:
        raise ValueError("invalid default answer: '%s'" % default)

    reply = None

    while not reply:
        sys.stdout.write(colorize(question, Colors.PROMPT) + prompt)

        choice = input().lower()
        reply = None

        if default and not choice:
            reply = default
        elif choice in valid:
            reply = valid[choice]
        else:
            print_failure("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")

    return reply == "yes"


def is_valid_user_provided_domain_format(domain):
    """
    Check whether a provided domain is valid.

    Parameters
    ----------
    domain : str
        The domain against which to check.

    Returns
    -------
    valid_domain : bool
        Whether or not the domain provided is valid.
    """

    if domain == "":
        print("You didn't enter a domain. Try again.")
        return False

    domain_regex = re.compile(r"www\d{0,3}[.]|https?")

    if domain_regex.match(domain):
        print(
            "The domain " + domain + " is not valid. Do not include "
            "www.domain.com or http(s)://domain.com. Try again."
        )
        return False
    else:
        return True


def recursive_glob(stem, file_pattern):
    """
    Recursively match files in a directory according to a pattern.

    Parameters
    ----------
    stem : str
        The directory in which to recurse
    file_pattern : str
        The filename regex pattern to which to match.

    Returns
    -------
    matches_list : list
        A list of filenames in the directory that match the file pattern.
    """

    if sys.version_info >= (3, 5):
        return glob(stem + "/**/" + file_pattern, recursive=True)
    else:
        # gh-316: this will avoid invalid unicode comparisons in Python 2.x
        if stem == str("*"):
            stem = "."
        matches = []
        for root, dirnames, filenames in os.walk(stem):
            for filename in fnmatch.filter(filenames, file_pattern):
                matches.append(path_join_robust(root, filename))
    return matches


def path_join_robust(path, *paths):
    """
    Wrapper around `os.path.join` with handling for locale issues.

    Parameters
    ----------
    path : str
        The first path to join.
    paths : varargs
        Subsequent path strings to join.

    Returns
    -------
    joined_path : str
        The joined path string of the two path inputs.

    Raises
    ------
    locale.Error : A locale issue was detected that prevents path joining.
    """

    try:
        # gh-316: joining unicode and str can be saddening in Python 2.x
        path = str(path)
        paths = [str(another_path) for another_path in paths]

        return os.path.join(path, *paths)
    except UnicodeDecodeError as e:
        raise locale.Error(
            "Unable to construct path. This is likely a LOCALE issue:\n\n" + str(e)
        )


# Colors
class Colors(object):
    PROMPT = "\033[94m"
    SUCCESS = "\033[92m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"


def supports_color():
    """
    Check whether the running terminal or command prompt supports color.

    Inspired by StackOverflow link (and Django implementation) here:

    https://stackoverflow.com/questions/7445658

    Returns
    -------
    colors_supported : bool
        Whether the running terminal or command prompt supports color.
    """

    sys_platform = sys.platform
    supported = sys_platform != "Pocket PC" and (
        sys_platform != "win32" or "ANSICON" in os.environ
    )

    atty_connected = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
    return supported and atty_connected


def colorize(text, color):
    """
    Wrap a string so that it displays in a particular color.

    This function adds a prefix and suffix to a text string so that it is
    displayed as a particular color, either in command prompt or the terminal.

    If the running terminal or command prompt does not support color, the
    original text is returned without being wrapped.

    Parameters
    ----------
    text : str
        The message to display.
    color : str
        The color string prefix to put before the text.

    Returns
    -------
    wrapped_str : str
        The wrapped string to display in color, if possible.
    """

    if not supports_color():
        return text

    return color + text + Colors.ENDC


def print_success(text):
    """
    Print a success message.

    Parameters
    ----------
    text : str
        The message to display.
    """

    print(colorize(text, Colors.SUCCESS))


def print_failure(text):
    """
    Print a failure message.

    Parameters
    ----------
    text : str
        The message to display.
    """

    print(colorize(text, Colors.FAIL))


# End Helper Functions


if __name__ == "__main__":
    main()
