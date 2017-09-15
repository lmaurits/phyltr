import fileinput

from phyltr.plumbing.sources import NewickParser, ComplexNewickParser

def test_parsing():
    lines = fileinput.input("tests/treefiles/basic.trees")
    trees = NewickParser().consume(lines)
    assert sum((1 for t in trees)) == 6

def test_internal_name_parsing():
    lines = fileinput.input("tests/treefiles/internal_names.trees")
    trees = NewickParser().consume(lines)
    assert sum((1 for t in trees)) == 6

def test_complex_parser_on_non_newick():
    lines = fileinput.input("tests/treefiles/internal_names.trees")
    trees = ComplexNewickParser().consume(lines)
    assert sum((1 for t in trees)) == 6

def test_complex_parser_on_non_tree():
    lines = fileinput.input("tests/treefiles/not_trees.trees")
    trees = ComplexNewickParser().consume(lines)
    print(list(trees))
    assert sum((1 for t in trees)) == 0
