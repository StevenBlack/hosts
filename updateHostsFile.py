#!/usr/bin/env python

# Script by Ben Limmer
# https://github.com/l1m5
#
# This Python script will combine all the host files you provide
# as sources into one, unique host file to keep you internet browsing happy.

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from glob import glob

import os
import locale
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
import fnmatch
import argparse
import socket
import json
import zipfile

# Detecting Python 3 for version-dependent implementations
PY3 = sys.version_info >= (3, 0)

if PY3:
    from urllib.request import urlopen
    raw_input = input
else:  # Python 2
    from urllib2 import urlopen


# Syntactic sugar for "sudo" command in UNIX / Linux
SUDO = "/usr/bin/sudo"


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
        "keepdomaincomments": False,
        "extensionspath": path_join_robust(BASEDIR_PATH, "extensions"),
        "extensions": [],
        "outputsubfolder": "",
        "hostfilename": "hosts",
        "targetip": "0.0.0.0",
        "ziphosts": False,
        "sourcedatafilename": "update.json",
        "sourcesdata": [],
        "readmefilename": "readme.md",
        "readmetemplate": path_join_robust(BASEDIR_PATH,
                                           "readme_template.md"),
        "readmedata": {},
        "readmedatafilename": path_join_robust(BASEDIR_PATH,
                                               "readmeData.json"),
        "exclusionpattern": "([a-zA-Z\d-]+\.){0,}",
        "exclusionregexs": [],
        "exclusions": [],
        "commonexclusions": ["hulu.com"],
        "blacklistfile": path_join_robust(BASEDIR_PATH, "blacklist"),
        "whitelistfile": path_join_robust(BASEDIR_PATH, "whitelist")}
# End Project Settings


def main():
    parser = argparse.ArgumentParser(description="Creates a unified hosts "
                                                 "file from hosts stored in "
                                                 "data subfolders.")
    parser.add_argument("--auto", "-a", dest="auto", default=False,
                        action="store_true", help="Run without prompting.")
    parser.add_argument("--backup", "-b", dest="backup", default=False,
                        action="store_true", help="Backup the hosts "
                                                  "files before they "
                                                  "are overridden.")
    parser.add_argument("--extensions", "-e", dest="extensions", default=[],
                        nargs="*", help="Host extensions to include "
                                        "in the final hosts file.")
    parser.add_argument("--ip", "-i", dest="targetip", default="0.0.0.0",
                        help="Target IP address. Default is 0.0.0.0.")
    parser.add_argument("--keepdomaincomments", "-k",
                        dest="keepdomaincomments", default=False,
                        help="Keep domain line comments.")
    parser.add_argument("--zip", "-z", dest="ziphosts", default=False,
                        action="store_true", help="Additionally create "
                                                  "a zip archive of the "
                                                  "hosts file.")
    parser.add_argument("--noupdate", "-n", dest="noupdate", default=False,
                        action="store_true", help="Don't update from "
                                                  "host data sources.")
    parser.add_argument("--skipstatichosts", "-s", dest="skipstatichosts",
                        default=False, action="store_true",
                        help="Skip static localhost entries "
                             "in the final hosts file.")
    parser.add_argument("--output", "-o", dest="outputsubfolder", default="",
                        help="Output subfolder for generated hosts file.")
    parser.add_argument("--replace", "-r", dest="replace", default=False,
                        action="store_true", help="Replace your active "
                                                  "hosts file with this "
                                                  "new hosts file.")
    parser.add_argument("--flush-dns-cache", "-f", dest="flushdnscache",
                        default=False, action="store_true",
                        help="Attempt to flush DNS cache "
                             "after replacing the hosts file.")

    global settings

    options = vars(parser.parse_args())

    options["outputpath"] = path_join_robust(BASEDIR_PATH,
                                             options["outputsubfolder"])
    options["freshen"] = not options["noupdate"]

    settings = get_defaults()
    settings.update(options)

    settings["sources"] = list_dir_no_hidden(settings["datapath"])
    settings["extensionsources"] = list_dir_no_hidden(
        settings["extensionspath"])

    # All our extensions folders...
    settings["extensions"] = [os.path.basename(item) for item in
                              list_dir_no_hidden(settings["extensionspath"])]
    # ... intersected with the extensions passed-in as arguments, then sorted.
    settings["extensions"] = sorted(list(
        set(options["extensions"]).intersection(settings["extensions"])))

    with open(settings["readmedatafilename"], "r") as f:
        settings["readmedata"] = json.load(f)

    prompt_for_update()
    prompt_for_exclusions()

    merge_file = create_initial_file()
    remove_old_hosts_file()

    final_file = remove_dups_and_excl(merge_file)
    write_opening_header(final_file)
    final_file.close()

    if settings["ziphosts"]:
        zf = zipfile.ZipFile(path_join_robust(settings["outputsubfolder"],
                                              "hosts.zip"), mode='w')
        zf.write(path_join_robust(settings["outputsubfolder"], "hosts"),
                 compress_type=zipfile.ZIP_DEFLATED, arcname='hosts')
        zf.close()

    update_readme_data()
    print_success("Success! The hosts file has been saved in folder " +
                  settings["outputsubfolder"] + "\nIt contains " +
                  "{:,}".format(settings["numberofrules"]) +
                  " unique entries.")

    prompt_for_move(final_file)


# Prompt the User
def prompt_for_update():
    """
    Prompt the user to update all hosts files.
    """

    # Create hosts file if it doesn't exist.
    if not os.path.isfile(path_join_robust(BASEDIR_PATH, "hosts")):
        try:
            open(path_join_robust(BASEDIR_PATH, "hosts"), "w+").close()
        except:
            print_failure("ERROR: No 'hosts' file in the folder,"
                          "try creating one manually")

    if not settings["freshen"]:
        return

    prompt = "Do you want to update all data sources?"
    if settings["auto"] or query_yes_no(prompt):
        update_all_sources()
    elif not settings["auto"]:
        print("OK, we'll stick with what we've  got locally.")


def prompt_for_exclusions():
    """
    Prompt the user to exclude any custom domains from being blocked.
    """

    prompt = ("Do you want to exclude any domains?\n"
              "For example, hulu.com video streaming must be able to access "
              "its tracking and ad servers in order to play video.")

    if not settings["auto"]:
        if query_yes_no(prompt):
            display_exclusion_options()
        else:
            print("OK, we'll only exclude domains in the whitelist.")


def prompt_for_flush_dns_cache():
    """
    Prompt the user to flush the DNS cache.
    """

    if settings["flushdnscache"]:
        flush_dns_cache()

    if not settings["auto"]:
        if query_yes_no("Attempt to flush the DNS cache?"):
            flush_dns_cache()


def prompt_for_move(final_file):
    """
    Prompt the user to move the newly created hosts file to its designated
    location in the OS.

    Parameters
    ----------
    final_file : file
        The file object that contains the newly created hosts data.
    """

    if settings["replace"] and not settings["skipstatichosts"]:
        move_file = True
    elif settings["auto"] or settings["skipstatichosts"]:
        move_file = False
    else:
        prompt = ("Do you want to replace your existing hosts file " +
                  "with the newly generated file?")
        move_file = query_yes_no(prompt)

    if move_file:
        move_hosts_file_into_place(final_file)
        prompt_for_flush_dns_cache()
# End Prompt the User


# Exclusion logic
def display_exclusion_options():
    """
    Display the exclusion options to the user.

    This function checks whether a user wants to exclude particular domains,
    and if so, excludes them.
    """

    for exclusion_option in settings["commonexclusions"]:
        prompt = "Do you want to exclude the domain " + exclusion_option + " ?"

        if query_yes_no(prompt):
            exclude_domain(exclusion_option)
        else:
            continue

    if query_yes_no("Do you want to exclude any other domains?"):
        gather_custom_exclusions()


def gather_custom_exclusions():
    """
    Gather custom exclusions from the user.
    """

    # We continue running this while-loop until the user
    # says that they have no more domains to exclude.
    while True:
        domain_prompt = ("Enter the domain you want "
                         "to exclude (e.g. facebook.com): ")
        user_domain = raw_input(domain_prompt)

        if is_valid_domain_format(user_domain):
            exclude_domain(user_domain)

        continue_prompt = "Do you have more domains you want to enter?"
        if not query_yes_no(continue_prompt):
            return


def exclude_domain(domain):
    """
    Exclude a domain from being blocked.

    Parameters
    ----------
    domain : str
        The filename or regex pattern to exclude.
    """

    settings["exclusionregexs"].append(re.compile(
        settings["exclusionpattern"] + domain))


def matches_exclusions(stripped_rule):
    """
    Check whether a rule matches an exclusion rule we already provided.

    If this function returns True, that means this rule should be excluded
    from the final hosts file.

    Parameters
    ----------
    stripped_rule : str
        The rule that we are checking.

    Returns
    -------
    matches_exclusion : bool
        Whether or not the rule string matches a provided exclusion.
    """

    stripped_domain = stripped_rule.split()[1]
    for exclusionRegex in settings["exclusionregexs"]:
        if exclusionRegex.search(stripped_domain):
            return True
    return False
# End Exclusion Logic


# Update Logic
def update_all_sources():
    """
    Update all host files, regardless of folder depth.
    """

    all_sources = recursive_glob("*", settings["sourcedatafilename"])

    for source in all_sources:
        update_file = open(source, "r")
        update_data = json.load(update_file)
        update_url = update_data["url"]
        update_file.close()

        print("Updating source " + os.path.dirname(
            source) + " from " + update_url)

        try:
            updated_file = get_file_by_url(update_url)

            # get rid of carriage-return symbols
            updated_file = updated_file.replace("\r", "")

            hosts_file = open(path_join_robust(BASEDIR_PATH,
                                               os.path.dirname(source),
                                               settings["hostfilename"]), "wb")
            write_data(hosts_file, updated_file)
            hosts_file.close()
        except:
            print("Error in updating source: ", update_url)
# End Update Logic


# File Logic
def create_initial_file():
    """
    Initialize the file in which we merge all host files for later pruning.
    """

    merge_file = tempfile.NamedTemporaryFile()

    # spin the sources for the base file
    for source in recursive_glob(settings["datapath"],
                                 settings["hostfilename"]):
        with open(source, "r") as curFile:
            write_data(merge_file, curFile.read())

    for source in recursive_glob(settings["datapath"],
                                 settings["sourcedatafilename"]):
        update_file = open(source, "r")
        update_data = json.load(update_file)
        settings["sourcesdata"].append(update_data)
        update_file.close()

    # spin the sources for extensions to the base file
    for source in settings["extensions"]:
        for filename in recursive_glob(path_join_robust(
                settings["extensionspath"], source), settings["hostfilename"]):
            with open(filename, "r") as curFile:
                write_data(merge_file, curFile.read())

        for update_file_path in recursive_glob(path_join_robust(
                settings["extensionspath"], source),
                settings["sourcedatafilename"]):
            update_file = open(update_file_path, "r")
            update_data = json.load(update_file)

            settings["sourcesdata"].append(update_data)
            update_file.close()

    if os.path.isfile(settings["blacklistfile"]):
        with open(settings["blacklistfile"], "r") as curFile:
            write_data(merge_file, curFile.read())

    return merge_file


def remove_dups_and_excl(merge_file):
    """
    Remove duplicates and remove hosts that we are excluding.

    We check for duplicate hostnames as well as remove any hostnames that
    have been explicitly excluded by the user.

    Parameters
    ----------
    merge_file : file
        The file object that contains the hostnames that we are pruning.
    """

    number_of_rules = settings["numberofrules"]
    if os.path.isfile(settings["whitelistfile"]):
        with open(settings["whitelistfile"], "r") as ins:
            for line in ins:
                line = line.strip(" \t\n\r")
                if line and not line.startswith("#"):
                    settings["exclusions"].append(line)

    if not os.path.exists(settings["outputpath"]):
        os.makedirs(settings["outputpath"])

    # Another mode is required to read and write the file in Python 3
    final_file = open(path_join_robust(settings["outputpath"], "hosts"),
                      "w+b" if PY3 else "w+")

    merge_file.seek(0)  # reset file pointer
    hostnames = {"localhost", "localhost.localdomain",
                 "local", "broadcasthost"}
    exclusions = settings["exclusions"]

    for line in merge_file.readlines():
        write_line = True

        # Explicit encoding
        line = line.decode("UTF-8")

        # replace tabs with space
        line = line.replace("\t+", " ")

        # see gh-271: trim trailing whitespace, periods
        line = line.rstrip(' .') + "\n"

        # Testing the first character doesn't require startswith
        if line[0] == "#" or re.match(r'^\s*$', line[0]):
            write_data(final_file, line)
            continue
        if "::1" in line:
            continue

        stripped_rule = strip_rule(line)  # strip comments
        if not stripped_rule or matches_exclusions(stripped_rule):
            continue

        # Normalize rule
        hostname, normalized_rule = normalize_rule(stripped_rule)
        for exclude in exclusions:
            if re.search('[\s\.]' + re.escape(exclude) + '\s', line):
                write_line = False
                break

        if normalized_rule and (hostname not in hostnames) and write_line:
            write_data(final_file, normalized_rule)
            hostnames.add(hostname)
            number_of_rules += 1

    settings["numberofrules"] = number_of_rules
    merge_file.close()

    return final_file


def normalize_rule(rule):
    """
    Standardize and format the rule string provided.

    Parameters
    ----------
    rule : str
        The rule whose spelling and spacing we are standardizing.

    Returns
    -------
    normalized_rule : str
        The rule string with spelling and spacing reformatted.
    """

    result = re.search(r'^\s*(\d{1,3}\.){3}\d{1,3}\s+([\w\.-]+[a-zA-Z])(.*)',
                       rule)
    if result:
        hostname, suffix = result.group(2, 3)

        # Explicitly lowercase and trim the hostname
        hostname = hostname.lower().strip()
        if suffix and settings["keepdomaincomments"]:
            # add suffix as comment only, not as a separate host
            return hostname, "%s %s #%s\n" % (settings["targetip"],
                                              hostname, suffix)
        else:
            return hostname, "%s %s\n" % (settings["targetip"], hostname)
    print("==>%s<==" % rule)
    return None, None


def strip_rule(line):
    """
    Sanitize a rule string provided before writing it to the output hosts file.

    Some sources put comments around their rules, for accuracy we need
    to strip them the comments are preserved in the output hosts file.

    Parameters
    ----------
    line : str
        The rule provided for sanitation.

    Returns
    -------
    sanitized_line : str
        The sanitized rule.
    """

    split_line = line.split()
    if len(split_line) < 2:
        # just return blank
        return ""
    else:
        return split_line[0] + " " + split_line[1]


def write_opening_header(final_file):
    """
    Write the header information into the newly-created hosts file.

    Parameters
    ----------
    final_file : file
        The file object that points to the newly-created hosts file.
    """

    final_file.seek(0)  # reset file pointer
    file_contents = final_file.read()  # save content
    final_file.seek(0)  # write at the top
    write_data(final_file, "# This hosts file is a merged collection "
                           "of hosts from reputable sources,\n")
    write_data(final_file, "# with a dash of crowd sourcing via Github\n#\n")
    write_data(final_file, "# Date: " + time.strftime(
        "%B %d %Y", time.gmtime()) + "\n")
    if settings["extensions"]:
        write_data(final_file, "# Extensions added to this file: " + ", ".join(
            settings["extensions"]) + "\n")
    write_data(final_file, "# Number of unique domains: " + "{:,}\n#\n".format(
        settings["numberofrules"]))
    write_data(final_file, "# Fetch the latest version of this file: "
                           "https://raw.githubusercontent.com/"
                           "StevenBlack/hosts/master/" +
               path_join_robust(settings["outputsubfolder"], "") + "hosts\n")
    write_data(final_file, "# Project home page: https://github.com/"
                           "StevenBlack/hosts\n#\n")
    write_data(final_file, "# ==============================="
                           "================================\n")
    write_data(final_file, "\n")

    if not settings["skipstatichosts"]:
        write_data(final_file, "127.0.0.1 localhost\n")
        write_data(final_file, "127.0.0.1 localhost.localdomain\n")
        write_data(final_file, "127.0.0.1 local\n")
        write_data(final_file, "255.255.255.255 broadcasthost\n")
        write_data(final_file, "::1 localhost\n")
        write_data(final_file, "fe80::1%lo0 localhost\n")
        write_data(final_file, "0.0.0.0 0.0.0.0\n")
        if platform.system() == "Linux":
            write_data(final_file, "127.0.1.1 " + socket.gethostname() + "\n")
            write_data(final_file, "127.0.0.53 " + socket.gethostname() + "\n")
        write_data(final_file, "\n")

    preamble = path_join_robust(BASEDIR_PATH, "myhosts")
    if os.path.isfile(preamble):
        with open(preamble, "r") as f:
            write_data(final_file, f.read())

    final_file.write(file_contents)


def update_readme_data():
    """
    Update the host and website information provided in the README JSON data.
    """

    extensions_key = "base"
    if settings["extensions"]:
        extensions_key = "-".join(settings["extensions"])

    generation_data = {"location": path_join_robust(
        settings["outputsubfolder"], ""),
                       "entries": settings["numberofrules"],
                       "sourcesdata": settings["sourcesdata"]}
    settings["readmedata"][extensions_key] = generation_data
    with open(settings["readmedatafilename"], "w") as f:
        json.dump(settings["readmedata"], f)


def move_hosts_file_into_place(final_file):
    """
    Move the newly-created hosts file into its correct location on the OS.

    For UNIX systems, the hosts file is "etc/hosts." On Windows, it's
    "C:\Windows\System32\drivers\etc\hosts."

    For this move to work, you must have administrator privileges to do this.
    On UNIX systems, this means having "sudo" access, and on Windows, it
    means being able to run command prompt in administrator mode.

    Parameters
    ----------
    final_file : file object
        The newly-created hosts file to move.
    """

    filename = os.path.abspath(final_file.name)

    if os.name == "posix":
        print("Moving the file requires administrative privileges. "
              "You might need to enter your password.")
        if subprocess.call([SUDO, "cp", filename, "/etc/hosts"]):
            print_failure("Moving the file failed.")
    elif os.name == "nt":
        print("Automatically moving the hosts file "
              "in place is not yet supported.")
        print("Please move the generated file to "
              "%SystemRoot%\system32\drivers\etc\hosts")


def flush_dns_cache():
    """
    Flush the DNS cache.
    """

    print("Flushing the DNS cache to utilize new hosts file...")
    print("Flushing the DNS cache requires administrative privileges. " +
          "You might need to enter your password.")

    dns_cache_found = False

    if platform.system() == "Darwin":
        if subprocess.call([SUDO, "killall", "-HUP", "mDNSResponder"]):
            print_failure("Flushing the DNS cache failed.")
    elif os.name == "nt":
        print("Automatically flushing the DNS cache is not yet supported.")
        print("Please copy and paste the command 'ipconfig /flushdns' in "
              "administrator command prompt after running this script.")
    else:
        nscd_prefixes = ["/etc", "/etc/rc.d"]
        nscd_msg = "Flushing the DNS cache by restarting nscd {result}"

        for nscd_prefix in nscd_prefixes:
            nscd_cache = nscd_prefix + "/init.d/nscd"

            if os.path.isfile(nscd_cache):
                dns_cache_found = True

                if subprocess.call([SUDO, nscd_cache, "restart"]):
                    print_failure(nscd_msg.format(result="failed"))
                else:
                    print_success(nscd_msg.format(result="succeeded"))

        system_prefixes = ["/usr", ""]
        service_types = ["NetworkManager", "wicd", "dnsmasq", "networking"]

        for system_prefix in system_prefixes:
            systemctl = system_prefix + "/bin/systemctl"
            system_dir = system_prefix + "/lib/systemd/system"

            for service_type in service_types:
                service = service_type + ".service"
                service_file = path_join_robust(system_dir, service)
                service_msg = ("Flushing the DNS cache by "
                               "restarting " + service + " {result}")

                if os.path.isfile(service_file):
                    dns_cache_found = True

                    if subprocess.call([SUDO, systemctl, "restart", service]):
                        print_failure(service_msg.format(result="failed"))
                    else:
                        print_success(service_msg.format(result="succeeded"))

        dns_clean_file = "/etc/init.d/dns-clean"
        dns_clean_msg = ("Flushing the DNS cache via "
                         "dns-clean executable {result}")

        if os.path.isfile(dns_clean_file):
            dns_cache_found = True

            if subprocess.call([SUDO, dns_clean_file, "start"]):
                print_failure(dns_clean_msg.format(result="failed"))
            else:
                print_success(dns_clean_msg.format(result="succeeded"))

        if not dns_cache_found:
            print_failure("Unable to determine DNS management tool.")


def remove_old_hosts_file():
    """
    Remove the old hosts file.

    This is a hotfix because merging with an already existing hosts file leads
    to artifacts and duplicates.
    """

    old_file_path = path_join_robust(BASEDIR_PATH, "hosts")
    # create if already removed, so remove wont raise an error
    open(old_file_path, "a").close()

    if settings["backup"]:
        backup_file_path = path_join_robust(BASEDIR_PATH, "hosts-{}".format(
            time.strftime("%Y-%m-%d-%H-%M-%S")))

        # Make a backup copy, marking the date in which the list was updated
        shutil.copy(old_file_path, backup_file_path)

    os.remove(old_file_path)

    # Create new empty hosts file
    open(old_file_path, "a").close()
# End File Logic


# Helper Functions
def get_file_by_url(url):
    """
    Get a file data located at a particular URL.

    Parameters
    ----------
    url : str
        The URL at which to access the data.

    Returns
    -------
    url_data : str or None
        The data retrieved at that URL from the file. Returns None if the
        attempted retrieval is unsuccessful.
    """

    try:
        f = urlopen(url)
        return f.read().decode("UTF-8")
    except:
        print("Problem getting file: ", url)


def write_data(f, data):
    """
    Write data to a file object. This is a cross-Python implementation.

    Parameters
    ----------
    f : file
        The file object at which to write the data.
    data : str
        The data to write to the file.
    """

    if PY3:
        f.write(bytes(data, "UTF-8"))
    else:
        f.write(str(data).encode("UTF-8"))


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
    Ask a yes/no question via raw_input() and get answer from the user.

    Inspired by the following implementation:

    http://code.activestate.com/recipes/577058

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

    valid = {"yes": "yes", "y": "yes", "ye": "yes",
             "no": "no", "n": "no"}
    prompt = {None: " [y/n] ",
              "yes": " [Y/n] ",
              "no": " [y/N] "}.get(default, None)

    if not prompt:
        raise ValueError("invalid default answer: '%s'" % default)

    reply = None

    while not reply:
        sys.stdout.write(colorize(question, Colors.PROMPT) + prompt)

        choice = raw_input().lower()
        reply = None

        if default and not choice:
            reply = default
        elif choice in valid:
            reply = valid[choice]
        else:
            print_failure("Please respond with 'yes' or 'no' "
                          "(or 'y' or 'n').\n")

    return reply == "yes"


def is_valid_domain_format(domain):
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

    domain_regex = re.compile("www\d{0,3}[.]|https?")

    if domain_regex.match(domain):
        print("The domain " + domain +
              " is not valid. Do not include "
              "www.domain.com or http(s)://domain.com. Try again.")
        return False
    else:
        return True


def recursive_glob(stem, file_pattern):
    """
    Recursively match files in a directory according to a pattern.

    This function is a version-independent of Python 3.x's function:

    glob( ... "/**/" ... )

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
        raise locale.Error("Unable to construct path. This is "
                           "likely a LOCALE issue:\n\n" + str(e))


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
    supported = sys_platform != "Pocket PC" and (sys_platform != "win32"
                                                 or "ANSICON" in os.environ)

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
