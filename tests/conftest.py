import os
import fileinput

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


@pytest.fixture(scope='session')
def treefile(treefilepath):
    def lines(*fnames):
        return fileinput.input([treefilepath(fname) for fname in fnames])
    return lines


@pytest.fixture
def treefilenewick(treefile):
    def newick(fname):
        parser = NewickParser if fname.endswith('.trees') else ComplexNewickParser
        lines = treefile(fname)
        res = list(parser().consume(lines))
        # Note: NewickParser and ComplexNewickParser do not close the stream upon consumption!
        lines.close()
        return res
    return newick


@pytest.fixture
def basictrees(treefilenewick):
    return treefilenewick('basic.trees')
