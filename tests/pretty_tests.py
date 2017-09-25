import fileinput

from phyltr.plumbing.sources import NewickParser
from phyltr.main import build_pipeline
from phyltr.commands.pretty import Pretty

def test_init_from_args():
    pretty = Pretty.init_from_args("")
    assert pretty.compress == False
    assert pretty.label == "name"

    pretty = Pretty.init_from_args("--compress")
    assert pretty.compress == True

    pretty = Pretty.init_from_args("--label foo")
    assert pretty.label == "foo"

def test_pretty():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    for x in Pretty().consume(trees):
        assert type(x) == str

def test_pretty_compressed_low_signal():
    lines = fileinput.input("tests/treefiles/low_signal.trees")
    trees = NewickParser().consume(lines)
    for x in build_pipeline("support | pretty --compress", trees):
        assert type(x) == str

def test_pretty_compressed_mid_signal():
    lines = fileinput.input("tests/treefiles/mid_signal.trees")
    trees = NewickParser().consume(lines)
    for x in build_pipeline("support | pretty --compress", trees):
        assert type(x) == str
