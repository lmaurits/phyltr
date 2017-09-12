import phyltr.plumbing.helpers as helpers
from phyltr.commands.cat import Cat
from phyltr.commands.height import Height
from phyltr.commands.taxa import Taxa

def test_plumb_stdin():
    helpers.plumb_stdin(Cat(), "tests/treefiles/basic.trees")

def test_complex_plumb():
    helpers.complex_plumb(Cat(), "tests/treefiles/beast_output.nex")

def test_plumb_strings():
    helpers.plumb_strings(Height(), "tests/treefiles/basic.trees")

def test_plumb_list():
    helpers.plumb_list(Taxa(), "tests/treefiles/basic.trees")

def test_plumb_null():
    helpers.plumb_null(Cat(), "tests/treefiles/basic.trees")
