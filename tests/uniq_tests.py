import fileinput
import shlex

from phyltr.plumbing.sources import NewickParser
from phyltr.commands.uniq import Uniq, init_from_args
from phyltr.commands.length import Length

def test_init_from_args():
    uniq, files = init_from_args([])
    assert uniq.lengths == "mean"

    for lengths in ("min", "max", "median"):
        uniq, files = init_from_args(shlex.split("--lengths %s" % lengths))
        assert uniq.lengths == lengths

def test_uniq():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = list(NewickParser().consume(lines))
    uniq = Uniq().consume(trees)
    # The 6 basic trees comprise 5 unique topologies.
    # This is a pretty weak test, but...
    assert sum((1 for t in uniq)) == 5

def test_min_med_max_uniq():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = list(NewickParser().consume(lines))

    min_uniq = Uniq(lengths="min").consume(trees)
    min_lengths = Length().consume(min_uniq)

    med_uniq = Uniq(lengths="median").consume(trees)
    med_lengths = Length().consume(med_uniq)

    max_uniq = Uniq(lengths="max").consume(trees)
    max_lengths = Length().consume(max_uniq)

    for l, m, L in zip(min_lengths, med_lengths, max_lengths):
        assert l <= m <= L
