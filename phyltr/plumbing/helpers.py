import fileinput
import sys

from phyltr.plumbing.sources import NewickParser, ComplexNewickParser
from phyltr.plumbing.sinks import NewickFormatter, StringFormatter, ListPerLineFormatter

def plumb_stdin(command, files="-"):
    source = fileinput.input(files)
    trees_from_stdin = NewickParser().consume(source)
    output_trees = command.consume(trees_from_stdin)
    NewickFormatter(sys.stdout).consume(output_trees)

def complex_plumb(command, files="-"):
    source = fileinput.input(files)
    trees_from_stdin = ComplexNewickParser().consume(source)
    output_trees = command.consume(trees_from_stdin)
    NewickFormatter(sys.stdout).consume(output_trees)

def plumb_strings(command, files="-"):
    source = fileinput.input(files)
    trees_from_stdin = NewickParser().consume(source)
    output_trees = command.consume(trees_from_stdin)
    StringFormatter(sys.stdout).consume(output_trees)

def plumb_list(command, files="-"):
    source = fileinput.input(files)
    trees_from_stdin = NewickParser().consume(source)
    output_lists = command.consume(trees_from_stdin)
    ListPerLineFormatter(sys.stdout).consume(output_lists)

def plumb_null(command, files="-"):
    source = fileinput.input(files)
    trees_from_stdin = NewickParser().consume(source)
    output_trees = command.consume(trees_from_stdin)
    # Silently pull trees through the pipeline
    for t in output_trees:
        pass

