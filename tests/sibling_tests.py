import fileinput

from nose.tools import raises

from phyltr.main import build_pipeline
from phyltr.plumbing.sources import NewickParser
from phyltr.commands.sibling import Sibling

def test_init_from_args():
    sibling = Sibling.init_from_args("A")

@raises(ValueError)
def test_bad_init_no_args():
    Sibling()

def test_sibling():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = list(NewickParser().consume(lines))
    siblings = list(Sibling("A").consume(trees))
    assert siblings == ["B","C","B","B","C","B"]

def test_non_leaf_sibling():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = list(NewickParser().consume(lines))
    siblings = list(build_pipeline("sibling C", source=trees))
    print(siblings)
    assert siblings == ["(A,B)","A","(A,B)","(A,B)","A","E"]

@raises(ValueError)
def test_bad_params_missing_taxa():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = list(NewickParser().consume(lines))
    siblings = list(Sibling("X").consume(trees))
