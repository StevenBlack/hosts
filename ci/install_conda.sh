#!/bin/bash

set -e

if [ -d "$HOME/miniconda3" ] && [ -e "$HOME/miniconda3/bin/conda" ]; then
    echo "Miniconda install already present in cache: $HOME/miniconda3"
    rm -rf "$HOME"/miniconda3/envs/hosts  # Just in case...
else
    echo "Installing Miniconda..."
    rm -rf "$HOME"/miniconda3  # Just in case...

    if [ "$(uname)" == "Darwin" ]; then
        wget -nv https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh -O miniconda.sh
    else
        wget -nv https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
    fi

    bash miniconda.sh -b -p "$HOME/miniconda3"
fi

echo "Configuring Miniconda..."
conda config --set ssl_verify false
conda config --set always_yes true --set changeps1 false

echo "Updating Miniconda"
conda update conda
conda update --all
conda info -a
