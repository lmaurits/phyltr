import fileinput

from phyltr.plumbing.sources import NewickParser
from phyltr.commands.collapse import Collapse

def test_collapse():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = list(NewickParser().consume(lines))
    collapsed = Collapse({"left":("A","B","C"), "right":("D","E","F")}).consume(trees)
    # These groups are monophyletic in the first 5 of the 6 basic trees, so...
    for n, t in enumerate(collapsed):
        print(t)
        print(len(t.get_leaves()))
        assert len(t.get_leaves()) == (2 if n < 5 else 6)

