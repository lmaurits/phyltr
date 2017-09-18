import fileinput
import shlex

from phyltr.plumbing.sources import NewickParser
from phyltr.commands.pretty import Pretty, init_from_args

def test_init_from_args():
    pretty, files = init_from_args([])
    assert pretty.compress == False
    assert pretty.label == "name"

    pretty, files = init_from_args(shlex.split("--compress"))
    assert pretty.compress == True

    pretty, files = init_from_args(shlex.split("--label foo"))
    assert pretty.label == "foo"

def test_pretty():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    for x in Pretty().consume(trees):
        assert type(x) == str

def test_pretty_compressed():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    for x in Pretty(compress=True).consume(trees):
        assert type(x) == str

def test_pretty_compressed_low_signal():
    lines = fileinput.input("tests/treefiles/low_signal.trees")
    trees = NewickParser().consume(lines)
    for x in Pretty(compress=True).consume(trees):
        assert type(x) == str
