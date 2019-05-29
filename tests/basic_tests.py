import pytest

from phyltr.commands.cat import Cat
from phyltr import run_command
from phyltr.plumbing.sources import NewickParser, ComplexNewickParser


@pytest.mark.parametrize(
    'cmd,fname',
    [
        ('', None),
        ('--help', None),
        ('kill_all_humans', None),
        ('cat', 'basic.trees'),
        ('stat', 'basic.trees'),
        ('pretty', 'basic.trees'),
        ('height', 'basic.trees'),
        ('taxa', 'basic.trees'),
        ('prune', None),
        ('sibling', None),
    ]
)
def test_command(cmd, fname, treefilepath):
    if fname:
        cmd += ' {0}'.format(treefilepath(fname))
    run_command(cmd)


def test_command_bad_args():
    if 1:#with pytest.raises(ValueError):
        _ = Cat.init_from_args("cat --foobar")

def test_parsing(treefile):
    trees = NewickParser().consume(treefile('basic.trees'))
    assert sum((1 for t in trees)) == 6

def test_internal_name_parsing(treefile):
    trees = NewickParser().consume(treefile('internal_names.trees'))
    assert sum((1 for t in trees)) == 6

def test_complex_parser_on_non_newick(treefile):
    trees = ComplexNewickParser().consume(treefile('internal_names.trees'))
    assert sum((1 for t in trees)) == 6


def test_complex_parser_on_non_tree(treefile):
    trees = ComplexNewickParser().consume(treefile('not_trees.trees'))
    assert sum((1 for t in trees)) == 0

def test_beast_nexus_output(treefile):
    trees = ComplexNewickParser().consume(treefile('beast_output.nex'))
    assert sum([1 for t in trees]) == 10

def test_beast_nexus_burnin(treefile):
    trees = ComplexNewickParser(burnin=10).consume(treefile('beast_output.nex'))
    assert sum([1 for t in trees]) == 9
    trees = ComplexNewickParser(burnin=20).consume(treefile('beast_output.nex'))
    assert sum([1 for t in trees]) == 8

def test_beast_nexus_subsample(treefile):
    trees = ComplexNewickParser(subsample=2).consume(treefile('beast_output.nex'))
    assert sum([1 for t in trees]) == 5
    trees = ComplexNewickParser(subsample=5).consume(treefile('beast_output.nex'))
    assert sum([1 for t in trees]) == 2

def test_beast_nexus_burnin_and_subsample(treefile):
    trees = ComplexNewickParser(burnin=20, subsample=2).consume(treefile('beast_output.nex'))
    assert sum([1 for t in trees]) == 4
    trees = ComplexNewickParser(burnin=50, subsample=5).consume(treefile('beast_output.nex'))
    assert sum([1 for t in trees]) == 1

def test_burnin_with_files_of_unequal_length(treefile):
    trees = ComplexNewickParser(burnin=20).consume(treefile('basic.trees'))
    assert sum([1 for t in trees]) == 5
    trees = ComplexNewickParser(burnin=20).consume(treefile('beast_output.nex'))
    assert sum([1 for t in trees]) == 8
    trees = ComplexNewickParser(burnin=20).consume(treefile('beast_output.nex', 'basic.trees'))
    assert sum([1 for t in trees]) == 13
