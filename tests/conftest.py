import os
import fileinput
from contextlib import closing

import pytest

from phyltr.plumbing.sources import NewickParser, ComplexNewickParser


@pytest.fixture(scope='session')
def argfilepath():
    def path(fname):
        return os.path.join(os.path.dirname(__file__), 'argfiles', fname)
    return path


@pytest.fixture(scope='session')
def emptyargs(argfilepath):
    return argfilepath('empty.txt')


@pytest.fixture(scope='session')
def treefilepath():
    def path(fname):
        return os.path.join(os.path.dirname(__file__), 'treefiles', fname)
    return path


@pytest.fixture
def treefile(treefilepath):
    def lines(*fnames):
        with closing(fileinput.input([treefilepath(fname) for fname in fnames])) as fp:
            for line in fp:
                yield line
    return lines


@pytest.fixture
def treefilenewick(treefile):
    def newick(fname):
        parser = NewickParser if fname.endswith('.trees') else ComplexNewickParser
        return list(parser().consume(treefile(fname)))
    return newick


@pytest.fixture
def basictrees(treefilenewick):
    return treefilenewick('basic.trees')
