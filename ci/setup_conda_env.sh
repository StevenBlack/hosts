#!/bin/bash

set -e

echo "Creating a Python $PYTHON_VERSION environment"
conda create -n hosts python="$PYTHON_VERSION"
source activate hosts

echo "Installing packages..."
conda install flake8 beautifulsoup4 lxml
