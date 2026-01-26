import simpleimageio as sio
import os
from pathlib import Path
import sys
import tempfile


def here() -> Path:
    return Path(__file__).resolve().parent


def data_dir() -> Path:
    return here() / "data"


def module_dir() -> Path:
    return here().parent


def temp_output_dir() -> Path:
    dir_path = Path(tempfile.gettempdir()) / "pyoidn_tests"
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def read_image(name: str):
    return sio.read(str(data_dir() / name)).astype("float32")


def setup_module():
    """
    Add pyoidn to sys.path for local testing if PYOIDN_LOCAL_TESTS is set.
    """
    if os.environ.get("PYOIDN_LOCAL_TESTS") == "1":
        sys.path.insert(0, str(module_dir()))
