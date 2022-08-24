"""redast installation script"""

import runpy
from pathlib import Path

from setuptools import find_packages, setup  # type: ignore

NAME = "redast"
DESCRIPTION = "remote data storage"
LICENSE = "MIT"
AUTHOR = "Vladislav A. Proskurov"
AUTHOR_EMAIL = "rilshok@pm.me"
URL = "https://github.com/rilshok/redast"
CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]

VERSION_PATH = str(Path(__file__).resolve().parent / NAME / "__version__.py")
VERSION = runpy.run_path(VERSION_PATH)["__version__"]

with open("README.md", "r", encoding="utf-8") as file:
    LONG_DESCRIPTION = file.read()

with open("requirements.txt", "r", encoding="utf-8") as file:
    REQUIREMENTS = file.read().splitlines()


setup(
    name=NAME,
    descriprion=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    license=LICENSE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    version=VERSION,
    url=URL,
    packages=find_packages(include=(NAME,)),
    include_package_data=True,
    install_requires=REQUIREMENTS,
    classifiers=CLASSIFIERS,
    python_requires=">=3.8",
)
