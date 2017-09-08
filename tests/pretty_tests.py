import fileinput
import tempfile

from phyltr.commands.generic import NewickParser
from phyltr.commands.pretty import Pretty

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
