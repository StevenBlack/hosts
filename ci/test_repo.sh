#!/bin/bash

echo "Running unittests..."
source activate hosts

nosetests
