#!/bin/bash
set -e
if [ -d /state ]; then 
    .venv/bin/python3 generate.py
    pushd terraform
    tofu init
    tofu plan -out plan 
    tofu apply plan
    popd
else
    echo "No state persistance"
    exit 1
fi