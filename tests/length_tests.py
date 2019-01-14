from phyltr.commands.length import Length

def test_length(basictrees):
    lengths = Length().consume(basictrees)
    for l in lengths:
        assert type(l) == float
        assert l >= 0.0
