#!/bin/bash

echo "Linting repository..."
source activate hosts

if [ "$PYTHON_VERSION" = "2.7" ]; then
    echo "Skipping flake8 because it is broken on Python $PYTHON_VERSION"
else
    flake8 --max-line-length 120
fi
