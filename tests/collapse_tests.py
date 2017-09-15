import fileinput
import shlex

from nose.tools import raises

from phyltr.plumbing.sources import NewickParser
from phyltr.plumbing.helpers import build_pipeline
from phyltr.commands.annotate import Annotate
from phyltr.commands.collapse import Collapse, init_from_args

def test_init_from_args():
    collapse, files = init_from_args(shlex.split("--translate tests/argfiles/collapse.txt"))
    assert collapse.filename == "tests/argfiles/collapse.txt"

    collapse, files = init_from_args(shlex.split("--attribute collapsibility"))
    assert collapse.attribute == "collapsibility"

@raises(ValueError)
def test_bad_init_no_args():
    Collapse()

def test_collapse():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = list(NewickParser().consume(lines))
    collapsed = Collapse({"left":("A","B","C"), "right":("D","E","F")}).consume(trees)
    # These groups are monophyletic in the first 5 of the 6 basic trees, so...
    for n, t in enumerate(collapsed):
        assert len(t.get_leaves()) == (2 if n < 5 else 6)

def test_file_collapse():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = list(NewickParser().consume(lines))
    collapsed = Collapse(filename="tests/argfiles/collapse.txt").consume(trees)
    # These groups are monophyletic in the first 5 of the 6 basic trees, so...
    for n, t in enumerate(collapsed):
        assert len(t.get_leaves()) == (2 if n < 5 else 6)

def test_attribute_collapse():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = list(NewickParser().consume(lines))
    annotated = Annotate("tests/argfiles/annotation.csv", "taxon").consume(trees)
    # f1 in the annotations applied above corresponds to the same left/right
    # split as the other tests above
    collapsed = Collapse(attribute="f1").consume(annotated)
    # These groups are monophyletic in the first 5 of the 6 basic trees, so...
    for n, t in enumerate(collapsed):
        assert len(t.get_leaves()) == (2 if n < 5 else 6)

def test_attribute_singleton_collapse():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = list(NewickParser().consume(lines))
    collapsed = build_pipeline("annotate -f tests/argfiles/annotation.csv -k taxon | collapse --attribute f3", trees)
    for t in collapsed:
        assert len(t.get_leaves()) == 6

def test_non_collapse():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = list(NewickParser().consume(lines))
    collapsed = Collapse({"non-existent":("X","Y","Z")}).consume(trees)
    for t1, t2 in zip(trees, collapsed):
        assert t1.write() == t2.write()

def test_attribute_non_collapse():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = list(NewickParser().consume(lines))
    collapsed = Collapse(attribute="foo").consume(trees)
    for t1, t2 in zip(trees, collapsed):
        assert t1.write() == t2.write()
