#!/bin/bash

echo "Linting repository..."
source activate hosts

flake8
