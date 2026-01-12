from setuptools import setup, find_packages
import platform
import os
from pathlib import Path


def get_whl_platform():
    system = platform.system().lower()
    machine = platform.machine().lower()

    # Allow CI to override detected architecture (e.g., building arm64 wheel on Intel runner)
    target_arch = os.environ.get("TARGET_ARCH", "").lower()
    if target_arch != "":
        machine = target_arch

    if system == "darwin":
        if machine in ("arm64", "aarch64"):
            return "macosx_12_0_arm64"
        return "macosx_10_15_x86_64"
    elif system == "linux":
        return "manylinux2014_x86_64"
    elif system == "windows":
        return "win_amd64"
    else:
        raise RuntimeError(f"Unsupported platform: {system} {machine}")


def get_oidn_version() -> str:
    version = os.environ.get("VERSION")
    if version is None:
        raise RuntimeError("VERSION environment variable is not set.")
    return version


def write_version_py(version: str):
    """Write the OIDN/package version into pyoidn/version.py."""
    version_file = Path(__file__).parent / "pyoidn" / "version.py"
    # Keep existing API (oidn_version) to avoid breaking imports
    content = f'oidn_version = "{version}"\n'
    version_file.write_text(content, encoding="utf-8")


# Ensure pyoidn/version.py is synchronized with the distribution version
try:
    write_version_py(get_oidn_version())
except Exception as e:
    # Avoid failing the build if writing the version file encounters an unexpected issue
    print(f"Warning: failed to write pyoidn/version.py: {e}")

setup(
    name="pyoidn",
    version=get_oidn_version(),
    packages=find_packages(),
    package_data={
        "pyoidn": ["oidn/**"],
    },
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=["numpy", "cffi>=1.0.0"],
    author="Carbene Hu",
    author_email="hyikerhu0212@gmail.com",
    description="Intel Open Image Denoise(OIDN) python binding.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Hyiker/pyoidn",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Graphics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: C++",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Environment :: GPU",
        "Natural Language :: English",
    ],
    platforms=["Linux", "Windows", "macOS"],
    options={"bdist_wheel": {"plat_name": get_whl_platform()}},
)
