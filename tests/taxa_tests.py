import fileinput
import tempfile

from phyltr.plumbing.sources import NewickParser
from phyltr.commands.taxa import Taxa, init_from_args

def test_init_from_args():
    taxa, files = init_from_args([])

def test_taxa():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    for taxa in Taxa().consume(trees):
        assert taxa == ["A", "B", "C", "D", "E", "F"]
    lines.close()
