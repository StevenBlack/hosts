# Extensions

Use subfolders under the `extensions` folder to house extensions to the final amalgamated hosts file.

Currently this repo includes a `porn` extension which you can optionally add to your final amalgamated file.

Here's a sample call to include the `porn` extension.

**Using Python 3**:

    python3 updateHostsFile.py --extensions porn

or, in short form:

    python3 updateHostsFile.py -e porn

**Using Python 2.7**:

    python updateHostsFile.py --extensions porn

or, in short form:

    python updateHostsFile.py -e porn

More built-in extensions are coming soon.
