import pytest

from phyltr.main import build_pipeline
from phyltr.commands.annotate import Annotate
from phyltr.commands.collapse import Collapse

def test_init(argfilepath):
    collapse = Collapse.init_from_args("--translate {0}".format(argfilepath('collapse.txt')))
    assert collapse.opts.filename == argfilepath('collapse.txt')

    collapse = Collapse.init_from_args("--attribute collapsibility")
    assert collapse.opts.attribute == "collapsibility"

def test_bad_init_no_args():
    with pytest.raises(ValueError):
        Collapse()

def test_collapse(basictrees):
    collapsed = Collapse(
        clades={"left":("A","B","C"), "right":("D","E","F")}).consume(basictrees)
    # These groups are monophyletic in the first 5 of the 6 basic trees, so...
    for n, t in enumerate(collapsed):
        assert len(t.get_leaves()) == (2 if n < 5 else 6)

def test_file_collapse(basictrees, argfilepath):
    collapsed = Collapse(filename=argfilepath("collapse.txt")).consume(basictrees)
    # These groups are monophyletic in the first 5 of the 6 basic trees, so...
    for n, t in enumerate(collapsed):
        assert len(t.get_leaves()) == (2 if n < 5 else 6)

def test_attribute_collapse(basictrees):
    annotated = Annotate(
        filename="tests/argfiles/annotation.csv", key="taxon").consume(basictrees)
    # f1 in the annotations applied above corresponds to the same left/right
    # split as the other tests above
    collapsed = Collapse(attribute="f1").consume(annotated)
    # These groups are monophyletic in the first 5 of the 6 basic trees, so...
    for n, t in enumerate(collapsed):
        assert len(t.get_leaves()) == (2 if n < 5 else 6)

def test_attribute_singleton_collapse(treefilenewick, argfilepath):
    collapsed = build_pipeline(
        "annotate -f {0} -k taxon | collapse --attribute f3".format(argfilepath('annotation.csv')),
        treefilenewick('basic.trees'))
    for t in collapsed:
        assert len(t.get_leaves()) == 6

def test_non_collapse(basictrees):
    trees = list(basictrees)
    collapsed = Collapse({"non-existent":("X","Y","Z")}).consume(trees)
    for t1, t2 in zip(trees, collapsed):
        assert t1.write() == t2.write()

def test_attribute_non_collapse(basictrees):
    trees = list(basictrees)
    collapsed = Collapse(attribute="foo").consume(trees)
    for t1, t2 in zip(trees, collapsed):
        assert t1.write() == t2.write()
