#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from setuptools import setup, find_packages

version = {}
with open('turbosearch/version.py') as f:
    exec(f.read(), version)

setup(name='turbosearch',
      version=version['__version__'],
      description='Automated url finder',
      author='Hélvio Junior (M4v3r1ck)',
      author_email='helvio_junior@hotmail.com',
      url='https://github.com/helviojunior/turbosearch',
      packages=find_packages(),
      package_data={'turbosearch': ['resources/*']},
      install_requires=['bs4>=0.0.1', 'requests>=2.23.0', 'colorama'],
      entry_points= { 'console_scripts': [
        'turbosearch=turbosearch.turbosearch:run',
        'turbosearch_stats=turbosearch.turbosearch_stats:run',
        ]}
      )