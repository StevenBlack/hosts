#!/bin/bash

echo "Linting repository..."
source activate hosts

flake8 --max-line-length 120
