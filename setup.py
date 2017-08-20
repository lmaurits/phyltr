#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='phyltr',
    version='0.3.0',
    description='Unix filters for manipulating and analysing (samples of) phylogenetic trees represented in the Newick format',
    author='Luke Maurits',
    author_email='luke@maurits.id.au',
    url='https://github.com/lmaurits/phyltr',
    license="GPL3",
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],
    scripts=['bin/phyltr',],
    packages = ['phyltr','phyltr/commands', 'phyltr/utils'],
    requires=['ete2'],
    install_requires=['ete2']

)
