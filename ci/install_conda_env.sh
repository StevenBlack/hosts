#!/bin/bash

echo "Creating a Python $PYTHON_VERSION environment"
conda create -n hosts python=$PYTHON_VERSION || exit 1
source activate hosts

echo "Installing packages..."
conda install mock nose flake8
