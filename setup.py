#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='phyltr',
    version='0.1.0',
    description='Unix filters for manipulating and analysing (samples of) phylogenetic trees represented in the Newick format',
    author='Luke Maurits',
    author_email='luke@maurits.id.au',
    url='https://github.com/lmaurits/phyltr',
    license="BSD (2 clause)",
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
    ],
    scripts=['bin/phyltr',],
    packages = ['phyltr','phyltr/commands', 'phyltr/utils'],
    requires=['ete2'],
    install_requires=['ete2']

)
