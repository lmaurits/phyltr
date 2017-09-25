import fileinput

from nose.tools import raises

from phyltr.commands.cat import Cat
from phyltr.main import run_command
from phyltr.plumbing.sources import NewickParser, ComplexNewickParser

def test_no_command():
    run_command("")

def test_help():
    run_command("--help")

def test_bad_command():
    run_command("kill_all_humans")

def test_command():
    run_command("cat tests/treefiles/basic.trees")

def test_command_2():
    run_command("stat tests/treefiles/basic.trees")

def test_command_3():
    run_command("pretty tests/treefiles/basic.trees")

@raises(ValueError)
def test_command_bad_args():
    cat = Cat.init_from_args("cat --foobar")

def test_command_bad_args_2():
    run_command("prune")    # `prune` has a compulsory arg which is missing here

def test_string_formatter_command():
    run_command("height tests/treefiles/basic.trees")

def test_list_formatter_command():
    run_command("taxa tests/treefiles/basic.trees")

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
    assert sum((1 for t in trees)) == 0
