#!/bin/bash

python -m pip install --upgrade pip
pip install build

python -m bdist_wheel

pip install ./dist/*.whl
pip install -r requirements-test.txt

python tests/test.py
