from phyltr.commands.support import Support

def test_init_from_args():

    clades = Support.init_from_args("")
    assert clades.frequency == 0.0
    assert clades.ages == False
    assert clades.sort == False
    assert clades.filename == None
    
    clades = Support.init_from_args("-f 0.42")
    assert clades.frequency == 0.42

    clades = Support.init_from_args("--age")
    assert clades.ages == True

    clades = Support.init_from_args("--sort")
    assert clades.sort == True

def test_clades(basictrees):
    supported = Support(filename="/dev/null").consume(basictrees)
    for t in supported:
        for n in t.traverse():
            assert hasattr(n, "support")
            assert type(n.support) == float
            assert 0 <= n.support <= 1
