# Extensions

Use subfolders under the `extensions` folder to house extensions to the final unified hosts file.

Currently, this repo includes four extensions:

* `gambling` for common online betting sites,
* `social` for common social media sites,
* `porn` for porn sites, and
* `fakenews` for fake news sites.


Here are some sample calls, which vary which extensions are included.

**Using Python 3**:

    python3 updateHostsFile.py --auto --extensions porn social gambling

or, in short form:

    python3 updateHostsFile.py -a -e porn social gambling



**Using Python 2.7**:

    python updateHostsFile.py -auto --extensions porn social gambling

or, in short form:

    python updateHostsFile.py -a -e porn social gambling


More built-in extensions are coming soon.
