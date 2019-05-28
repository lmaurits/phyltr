from phyltr.main import build_pipeline
from phyltr.commands.pretty import Pretty

def test_init_from_args():
    pretty = Pretty.init_from_args("")
    assert pretty.opts.compress == False
    assert pretty.opts.label == "name"

    pretty = Pretty.init_from_args("--compress")
    assert pretty.opts.compress == True

    pretty = Pretty.init_from_args("--label foo")
    assert pretty.opts.label == "foo"

def test_pretty(basictrees):
    for x in Pretty().consume(basictrees):
        assert type(x) == str

def test_pretty_compressed_low_signal(treefilenewick):
    for x in build_pipeline("support | pretty --compress", treefilenewick('low_signal.trees')):
        assert type(x) == str

def test_pretty_compressed_mid_signal(treefilenewick):
    for x in build_pipeline("support | pretty --compress", treefilenewick('mid_signal.trees')):
        assert type(x) == str
