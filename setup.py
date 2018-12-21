#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='phyltr',
    version='dev',
    description='Unix filters for manipulating and analysing (samples of) phylogenetic trees represented in the Newick format',
    author='Luke Maurits',
    author_email='luke@maurits.id.au',
    url='https://github.com/lmaurits/phyltr',
    license="GPL3",
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],
    packages = ['phyltr','phyltr/commands', 'phyltr/plumbing', 'phyltr/utils'],
    entry_points = {
        'console_scripts': ['phyltr=phyltr.main:run_command'],
    },
    install_requires=['six', 'ete3'],
    extras_require={
        'dev': ['flake8', 'wheel', 'twine'],
        'test': [
            'mock',
            'pytest>=3.1',
            'pytest-mock',
            'pytest-cov',
            'coverage>=4.2',
        ],
    },
)
