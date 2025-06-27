#!/bin/bash
if [ -d /state ]; then 
    python3 /generate.py
    pushd terraform
    ls -la
    cat ganymede.tf
    popd
else
    echo "No state persistance"
    exit 1
fi