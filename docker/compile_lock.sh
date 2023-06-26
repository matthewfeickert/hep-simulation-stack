#!/bin/bash

python -m venv /venv
. /venv/bin/activate
python -m pip --no-cache-dir install --upgrade pip setuptools wheel
python -m pip --no-cache-dir install --upgrade pip-tools

cd docker
pip-compile \
    --generate-hashes \
    --output-file requirements.lock \
    --resolver=backtracking \
    requirements.txt
