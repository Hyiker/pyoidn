from setuptools import setup, find_packages
import platform


def get_whl_platform():
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == 'darwin':
        if machine == 'arm64':
            return 'macosx_12_0_arm64'
        return 'macosx_10_15_x86_64'
    elif system == 'linux':
        return 'manylinux2014_x86_64'
    elif system == 'windows':
        return 'win_amd64'
    else:
        raise RuntimeError(f"Unsupported platform: {system} {machine}")


setup(
    name="pyoidn",
    version="2.3.2",
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
    options={
        "bdist_wheel": {
            "plat_name": get_whl_platform()
        }
    }
)
