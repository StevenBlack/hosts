# Extensions

Use subfolders under the `extensions` folder to house extensions to the final unified hosts file.

Currently this repo includes two extensions: `social` for common social media sites, and `porn` for porn sites.  You can optionally add either or both to your final unified file.

Here's a sample call to include the `porn` extension.

**Using Python 3**:

    python3 updateHostsFile.py --extensions porn social

or, in short form:

    python3 updateHostsFile.py -e porn social

**Using Python 2.7**:

    python updateHostsFile.py --extensions porn social

or, in short form:

    python updateHostsFile.py -e porn social


More built-in extensions are coming soon.
