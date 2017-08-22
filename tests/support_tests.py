from __future__ import division

import fileinput

from phyltr.commands.generic import NewickParser
from phyltr.commands.support import Support

def test_clades():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    supported = Support().consume(trees)
    for t in supported:
        for n in t.traverse():
            assert hasattr(n, "support")
            assert type(n.support) == float
            assert 0 <= n.support <= 1
