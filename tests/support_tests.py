import fileinput
import shlex

from phyltr.plumbing.sources import NewickParser
from phyltr.commands.support import Support, init_from_args

def test_init_from_args():

    clades, files = init_from_args([])
    assert clades.frequency == 0.0
    assert clades.ages == False
    assert clades.sort == False
    assert clades.filename == None
    
    clades, files = init_from_args(["-f 0.42"])
    assert clades.frequency == 0.42

    clades, files = init_from_args(["--age"])
    assert clades.ages == True

    clades, files = init_from_args(["--sort"])
    assert clades.sort == True

def test_clades():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    supported = Support().consume(trees)
    for t in supported:
        for n in t.traverse():
            assert hasattr(n, "support")
            assert type(n.support) == float
            assert 0 <= n.support <= 1
