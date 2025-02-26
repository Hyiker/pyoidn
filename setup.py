from setuptools import setup, find_packages
import platform


def get_platform():
    system = platform.system().lower()

    if system == "linux":
        return "Linux"
    elif system == "darwin":
        return "Mac OS-X"
    elif system == "windows":
        return "Windows"
    else:
        raise OSError(f"Unsupported platform: {system}")


setup(
    name="pyoidn",
    version="2.3.0",
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
    platforms=[get_platform()],
)
