import fileinput

from nose.tools import raises

from phyltr.plumbing.sources import NewickParser
from phyltr.commands.grep import Grep

def test_init_from_args():
    grep = Grep.init_from_args("A,B,C")
    assert grep.taxa == set(("A","B","C"))
    assert grep.filename == None
    assert grep.inverse == False

    grep = Grep.init_from_args("A,B,C --inverse")
    assert grep.inverse == True

    grep = Grep.init_from_args("--file tests/argfiles/taxa_abc.txt")
    assert grep.taxa == set(("A","B","C"))
    assert grep.filename == "tests/argfiles/taxa_abc.txt"

@raises(ValueError)
def test_bad_init_no_args():
    Grep()

@raises(ValueError)
def test_bad_init_empty_file():
    Grep(filename="tests/argfiles/empty.txt")

def test_trivial_grep():
    """
    Test that grepping for all taxa in the tree just passes all trees.
    """

    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = list(NewickParser().consume(lines))
    grepped = list(Grep(["A","B","C","D","E","F"]).consume(trees))
    assert trees == grepped

def test_grep():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = list(NewickParser().consume(lines))
    grepper = Grep(["A","B"])
    grepped = grepper.consume(trees)
    # A and B are siblings in 4 of our standard testing trees
    assert sum((1 for t in grepped)) == 4
    grepped = grepper.consume(trees)
    assert all("A:1,B:1" in t.write() for t in grepped)

def test_inverse_grep():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = list(NewickParser().consume(lines))
    grepper = Grep(["A","B"], inverse=True)
    grepped = grepper.consume(trees)
    # A and B are siblings in 4/6 of our standard testing trees
    assert sum((1 for t in grepped)) == 2
    grepped = grepper.consume(trees)
    assert all("A:1,B:1" not in t.write() for t in grepped)

