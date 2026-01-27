from PIL import Image
import os
from pathlib import Path
import sys
import tempfile
import numpy as np


def here() -> Path:
    return Path(__file__).resolve().parent


def data_dir() -> Path:
    return here() / "data"


def module_dir() -> Path:
    return here().parent


def temp_output_dir() -> Path:
    dir_path = Path("tmp") / "pyoidn_tests"
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def read_image(name: str):
    return np.array(Image.open(data_dir() / name), dtype=np.float32) / 255.0

def is_local_test() -> bool:
    return os.environ.get("PYOIDN_LOCAL_TESTS") == "1"

def setup_module():
    """
    Add pyoidn to sys.path for local testing if PYOIDN_LOCAL_TESTS is set.
    """
    if is_local_test():
        sys.path.insert(0, str(module_dir()))
