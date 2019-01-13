#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from setuptools import setup, find_packages

NAME = "instabot"
DESCRIPTION = "Samu's little instabot."
URL = "https://github.com/astair/instabot.git"
AUTHOR = "Jonas Simon Fleck"
EMAIL = "jonas.simon.fleck@gmail.com"
REQUIRES_PYTHON = ">=3.6.0"
VERSION = "1.0"
LICENSE = "GPL-3.0"

# Python package requirements
REQUIRED = [
    "pyyaml>=3.13",
    "requests==2.20.0",
    "requests-toolbelt==0.7.0"
]

# Read README.md for long description
HERE = os.path.abspath(os.path.dirname(sys.argv[0]))

try:
    with open(os.path.join(HERE, "README.md"), "rt") as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

logs_dir = os.path.join(HERE, "logs/")
if not os.path.exists(logs_dir):
    os.mkdir(logs_dir)

setup(
    name = NAME,
    version = VERSION,
    url = URL,
    author = AUTHOR,
    license = LICENSE,
    author_email = EMAIL,
    long_description = long_description,
    description = DESCRIPTION,
    python_requires = REQUIRES_PYTHON,
    packages = find_packages(),
    install_requires = REQUIRED
)
