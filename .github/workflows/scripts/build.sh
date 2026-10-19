#!/bin/bash

python -m pip install --upgrade pip build wheel "setuptools>=65.6.1"

python setup.py bdist_wheel

pip install ./dist/*.whl
