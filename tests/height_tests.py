from phyltr.commands.height import Height

def test_height(basictrees):
    heights = Height().consume(basictrees)
    for h in heights:
        assert type(h) == float
        assert h >= 0.0
