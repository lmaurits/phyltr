import fileinput

from phyltr.commands.generic import NewickParser
from phyltr.commands.rename import Rename

def test_rename():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    renamed = Rename({"A":"X"}).consume(trees)
    for t in renamed:
        leaves = t.get_leaf_names()
        assert "A" not in leaves
        assert "X" in leaves
        assert all((x in leaves for x in ("B", "C", "D", "E", "F")))

def test_rename_with_remove():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    renamed = Rename({
        "A":"U",
        "B":"V",
        "D":"X",
        "E":"Y" }, remove=True).consume(trees)
    for t in renamed:
        leaves = t.get_leaf_names()
        assert all((x in leaves for x in ("U", "V", "X", "Y")))
        assert not any((x in leaves for x in ("A", "B", "C", "D", "E", "F")))

