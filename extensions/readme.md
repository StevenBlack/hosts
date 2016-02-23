# Extensions

Use subfolders under the `extensions` folder to house extensions for additional variants of the final amalgamated
hosts file.

Currently this repo includes a `porn` extension which you can optionally add to your final amalgamated file.

More built-in extensions are coming soon.

Here's a sample call to include the `porn` extension.

Using Python 3:

    python3 updateHostsFile.py [--auto] --extensions porn

Using Python 2.7:

    python updateHostsFile.py [--auto] --extensions porn
