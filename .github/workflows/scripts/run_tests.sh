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

python -c "import torch; import numpy; t = torch.tensor([1]); t.numpy()" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "Downgrading to NumPy < 2.0 to restore compatibility..."
    python -m pip install "numpy<2.0"
fi

python -m unittest discover ./tests/
