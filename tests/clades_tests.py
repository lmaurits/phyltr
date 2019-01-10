from __future__ import division

import fileinput

from phyltr.main import build_pipeline
from phyltr.plumbing.sources import NewickParser
from phyltr.commands.clades import Clades

def test_init_from_args():
    clades = Clades.init_from_args("")
    assert clades.frequency == 0.0
    assert clades.ages == False

    clades = Clades.init_from_args("--ages")
    assert clades.ages == True

    clades = Clades.init_from_args("-f 0.42")
    assert clades.frequency == 0.42

def test_clades():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    clades = Clades(ages=True)
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

def test_degenerate_clades(tmpdir):
    lines = fileinput.input("tests/treefiles/single_taxon.trees")
    trees = NewickParser().consume(lines)
    clades = Clades(ages=True)
    for t in clades.consume(trees):
        pass

def test_categorical_annotation():
    # This is just to make sure the clade probability calculator doesnt't
    # erroneously try to calculate means etc. of categorical annotations
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    for t in build_pipeline("annotate -f tests/argfiles/categorical_annotation.csv -k taxon | clades", trees):
        pass
