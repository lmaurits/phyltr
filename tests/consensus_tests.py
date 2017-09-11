from __future__ import division

import fileinput

from phyltr.plumbing.sources import NewickParser
from phyltr.commands.consensus import Consensus

def test_consensus():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    consensus = list(Consensus().consume(trees))
    assert len(consensus) == 1
