import pytest

from phyltr.commands.grep import Grep

def test_init_from_args(argfilepath):
    grep = Grep.init_from_args("A B C")
    assert grep.opts.taxa == {"A", "B", "C"}
    assert grep.opts.filename == None
    assert grep.opts.inverse == False

    grep = Grep.init_from_args("A B C --inverse")
    assert grep.opts.inverse == True

    taxa_abc = argfilepath('taxa_abc.txt')
    grep = Grep.init_from_args("--file {0}".format(taxa_abc))
    assert grep.opts.taxa == {"A", "B", "C"}
    assert grep.opts.filename == taxa_abc

    taxa_abc = argfilepath('argfile.csv')
    grep = Grep.init_from_args("--file {0} --column=COL1".format(taxa_abc))
    assert grep.opts.taxa == {"A", "B", "C"}

def test_bad_init_no_args():
    with pytest.raises(ValueError):
        Grep()

    with pytest.raises(ValueError):
        Grep(taxa=['A'])

def test_bad_init_empty_file(emptyargs):
    with pytest.raises(ValueError):
        Grep(filename=emptyargs)

def test_trivial_grep(basictrees):
    """
    Test that grepping for all taxa in the tree just passes all trees.
    """
    trees = list(basictrees)
    grepped = list(Grep(taxa=["A","B","C","D","E","F"]).consume(trees))
    assert trees == grepped

def test_grep(basictrees):
    trees = list(basictrees)
    grepper = Grep(taxa=["A","B"])
    grepped = grepper.consume(trees)
    # A and B are siblings in 4 of our standard testing trees
    assert sum((1 for t in grepped)) == 4
    grepped = grepper.consume(trees)
    assert all("A:1,B:1" in t.write() for t in grepped)

def test_inverse_grep(basictrees):
    trees = list(basictrees)
    grepper = Grep(taxa=["A","B"], inverse=True)
    grepped = grepper.consume(trees)
    # A and B are siblings in 4/6 of our standard testing trees
    assert sum((1 for t in grepped)) == 2
    grepped = grepper.consume(trees)
    assert all("A:1,B:1" not in t.write() for t in grepped)

