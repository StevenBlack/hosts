# PyInstaller build info

Running in a virtual environment in Windows, as admistrator, is a bit of a pain. Searching
the main repo, I found [issue 179](https://github.com/StevenBlack/hosts/issues/179)
that seemed to be exactly what I was after.

Sadly, that issue was closed without a PR being done, so I took a swing at it.

I used PyInstaller over py2exe because [py2exe doesn't seem to work after Python 3.4](https://stackoverflow.com/questions/41578808/python-indexerror-tuple-index-out-of-range-when-using-py2exe).

## Build "script"

I created build_exe.bat to handle the very complex process of building the exe and
moving it into the base build directory.

It's not elegant, but there are plenty of support files and I didn't want to
completely update the Python script just to make it work as an exe.

## Updated updateHostsWindows.bat

I also updated updateHostsWindows.bat to check for the existance of the exe file
and to run that if it exists. This means that if you don't want to compile to exe
there is no impact to existing setups.
