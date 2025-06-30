#!/bin/bash
set -e
if [ -d /state ]; then 
    .venv/bin/python3 generate.py
    pushd terraform
    terraform init
    terraform plan -out plan
    if [ "$APPLY" == "true" ]; then
       terraform apply plan
    fi
    popd
else
    echo "No state persistance"
    exit 1
fi