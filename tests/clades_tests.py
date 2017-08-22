from __future__ import division

import fileinput

from phyltr.commands.generic import NewickParser
from phyltr.commands.clades import Clades

def test_clades():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    clades = Clades()
    # Spin through all trees
    for t in clades.consume(trees):
        pass
    # Check that the computed probabilities agree
    # with hand calculated equivalents
    assert clades.cp.clade_probs["A,B"] == 4.0 / 6.0
    assert clades.cp.clade_probs["A,C"] == 2.0 / 6.0
    assert clades.cp.clade_probs["A,B,C"] == 5.0 / 6.0
    assert clades.cp.clade_probs["E,F"] == 3.0 / 6.0
    assert clades.cp.clade_probs["A,C"] == 2.0 / 6.0
    assert clades.cp.clade_probs["D,F"] == 1.0 / 6.0
    assert clades.cp.clade_probs["D,E"] == 1.0 / 6.0
    assert clades.cp.clade_probs["C,E"] == 1.0 / 6.0
    assert clades.cp.clade_probs["D,E,F"] == 5.0 / 6.0
    assert clades.cp.clade_probs["A,B,C,D,E,F"] == 6.0 / 6.0
