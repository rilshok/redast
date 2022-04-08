#!/usr/bin/env bash

stubgen ./redast -o .
python setup.py sdist bdist_wheel
twine upload --repository pypi dist/*
find redast -name "*.pyi" -type f -delete
rm -r dist build
