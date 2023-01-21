#!/usr/bin/python3
# -*- coding: UTF-8 -*-

'''
The build version is auto update by local git hook at .git/hooks/pre-push with the following content

#!/bin/bash

build=$(printf '0x%x' $(date +%s))
meta=$(cat turbosearch/__meta__.py | sed "s/__build__.*/__build__ = "${build}"/")
echo "$meta" > turbosearch/__meta__.py

git add ./turbosearch/__meta__.py
git commit -m "Update build version"

'''

import os
from setuptools import setup, find_packages

requires = [
    'bs4>=0.0.1', 
    'requests>=2.23.0', 
    'colorama', 
    'requests[socks]'
]

meta = {}
here = os.path.abspath(os.path.dirname(__file__))

with open('turbosearch/__meta__.py') as f:
    exec(f.read(), meta)

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

extra_files = package_files('turbosearch/resources')

setup(
    name=meta["__title__"],
    version=meta["__version__"],
    description=meta["__description__"],
    long_description=readme,
    long_description_content_type="text/markdown",
    author=meta["__author__"],
    author_email=meta["__author_email__"],
    url=meta["__url__"],
    packages=find_packages(),
    package_data={"": ["LICENSE" + extra_files]},
    include_package_data=True,
    python_requires=">=3.8, <4",
    install_requires=requires,
    license=meta["__license__"],
    readme="README.md",
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Security",
        "Topic :: System :: Networking",
        "Topic :: System :: Operating System",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities"
    ],
    entry_points={ 'console_scripts': [
        'turbosearch=turbosearch.turbosearch:run',
        'turbosearch_stats=turbosearch.turbosearch_stats:run',
    ]},
    project_urls={
        "Main Author": "https://sec4us.com.br/instrutores/helvio-junior/",
        "Documentation": meta["__url__"],
        "Source": meta["__url__"],
    },
)