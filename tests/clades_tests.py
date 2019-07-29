from phyltr import build_pipeline
from phyltr.commands.clades import Clades

def test_init_from_args():
    clades = Clades.init_from_args("")
    assert clades.opts.frequency == 0.0
    assert clades.opts.ages == False

    clades = Clades.init_from_args("--ages")
    assert clades.opts.ages == True

    clades = Clades.init_from_args("-f 0.42")
    assert clades.opts.frequency == 0.42

def test_clades(basictrees):
    clades = Clades(ages=True)
    # Spin through all trees
    list(clades.consume(basictrees))
    # Check that the computed probabilities agree
    # with hand calculated equivalents
    assert clades.cp.clade_probs["A B"] == 4.0 / 6.0
    assert clades.cp.clade_probs["A C"] == 2.0 / 6.0
    assert clades.cp.clade_probs["A B C"] == 5.0 / 6.0
    assert clades.cp.clade_probs["E F"] == 3.0 / 6.0
    assert clades.cp.clade_probs["A C"] == 2.0 / 6.0
    assert clades.cp.clade_probs["D F"] == 1.0 / 6.0
    assert clades.cp.clade_probs["D E"] == 1.0 / 6.0
    assert clades.cp.clade_probs["C E"] == 1.0 / 6.0
    assert clades.cp.clade_probs["D E F"] == 5.0 / 6.0
    assert clades.cp.clade_probs["A B C D E F"] == 6.0 / 6.0

def test_degenerate_clades(treefilenewick):
    clades = Clades(ages=True)
    list(clades.consume(treefilenewick('single_taxon.trees')))

def test_categorical_annotation(treefilenewick):
    # This is just to make sure the clade probability calculator doesnt't
    # erroneously try to calculate means etc. of categorical annotations
    list(build_pipeline(
        "annotate -f tests/argfiles/categorical_annotation.csv -k taxon | clades",
        treefilenewick('basic.trees')))
