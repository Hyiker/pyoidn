#!/bin/bash

# Run tests without torch
python -m pip install -r requirements-test.txt
python -m unittest discover ./tests/

# Run tests with torch
python -m pip install --upgrade pip
if [[ "${PLATFORM}" == "linux" || "${PLATFORM}" == "windows" ]]; then
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu --extra-index-url https://pypi.org/simple
else
# macOS wheels are available from the default index; keep it simple.
python -m pip install torch
fi
python -m unittest discover ./tests/
