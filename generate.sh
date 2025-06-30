#!/bin/bash
set -e
if [ -d /state ]; then 
    .venv/bin/python3 generate.py
    pushd terraform
    tofu init
    tofu plan -out plan
    if [ "$APPLY" == "true" ]; then
       tofu apply plan
    fi
    popd
else
    echo "No state persistance"
    exit 1
fi