#!/bin/bash
# Run tests with torch
python -m pip install --upgrade pip

# Run tests without torch
python -m pip install -r requirements-test.txt
python -m unittest discover ./tests/

if [[ "${PLATFORM}" == "linux" || "${PLATFORM}" == "windows" ]]; then
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu --extra-index-url https://pypi.org/simple
else
# macOS wheels are available from the default index; keep it simple.
python -m pip install torch
fi

# Disable test for x86_64 on macOS with torch due to lack of support.
if [[ "${PLATFORM}" == "macos" && "${ARCH}" == "x86_64" ]]; then
  exit 0
fi

python -m unittest discover ./tests/
