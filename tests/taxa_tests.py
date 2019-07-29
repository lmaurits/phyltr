from phyltr.commands.taxa import Taxa

def test_init_from_args():
    Taxa.init_from_args("")

def test_taxa(basictrees):
    for taxa in Taxa().consume(basictrees):
        assert taxa == ["A", "B", "C", "D", "E", "F"]
