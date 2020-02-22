# Contributing Guide

Contributing to Hosts is easy. This document shows you how to get started

## General

- The [Codebase Structure](https://github.com/StevenBlack/hosts/blob/master/codebase_structure.md) has
detailed information about how the various folders and files in this project are structured.

## Submitting changes

- Fork the repo
  - <https://github.com/StevenBlack/hosts/fork>
- Check out a new branch based and name it to what you intend to do:
  - Example:

    ```sh
    git checkout -b BRANCH_NAME
    ```

    If you get an error, you may need to fetch first, by using

    ```sh
    git remote update && git fetch
    ```

  - Use one branch per fix / feature
- Commit your changes
  - Please provide a git message that explains what you've done
  - Please make sure your commits follow the [conventions](https://gist.github.com/robertpainsi/b632364184e70900af4ab688decf6f53#file-commit-message-guidelines-md)
  - Commit to the forked repository
  - Example:

    ```sh
    git commit -am 'Add some fooBar'
    ```

- Push to the branch
  - Example:

    ```sh
    git push origin BRANCH_NAME
    ```

- Make a pull request
  - Make sure you send the PR to the `BRANCH_NAME` branch

If you follow these instructions, your Pull Request will land safely!
