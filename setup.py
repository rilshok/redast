import runpy
from pathlib import Path

from setuptools import find_packages, setup

name = "redast"
short_descriprion = "remote data storage"
author = "Vladislav A. Proskurov"
author_email = "rilshok@pm.me"
url = "https://github.com/rilshok/redast"
license = "MIT"
classifiers = [
    "Development Status :: 3 - Alpha",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]

version_path = Path(__file__).resolve().parent / name / "__version__.py"
version = runpy.run_path(version_path)["__version__"]

with open("README.md", "r") as file:
    long_description = file.read()

with open("requirements.txt", encoding="utf-8") as file:
    requirements = file.read().splitlines()

setup(
    name=name,
    author=author,
    author_email=author_email,
    descriprion=short_descriprion,
    long_description=long_description,
    long_description_content_type="text/markdown",
    license=license,
    url=url,
    packages=find_packages(include=(name,)),
    include_package_data=True,
    version=version,
    install_requires=requirements,
    classifiers=classifiers,
    python_requires=">=3.8",
)
