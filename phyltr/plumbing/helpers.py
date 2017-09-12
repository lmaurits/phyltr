import fileinput
import importlib
import shlex
import sys

from phyltr.plumbing.sources import NewickParser, ComplexNewickParser
from phyltr.plumbing.sinks import NewickFormatter, StringFormatter, ListPerLineFormatter

def build_pipeline(string, source):
    components = string.split("|")
    for n, args in enumerate(components):
        args = shlex.split(args)
        command = args[0]
        command_module = importlib.import_module("phyltr.commands."+command)
        print("Building this: ", args)
        command_obj, files = command_module.init_from_args(args[1:])
        if hasattr(command_obj, "taxa"):
            print(command_obj.taxa)
        if n==0:
            generator = command_obj.consume(source)
        else:
            generator = command_obj.consume(generator)
    return generator

def plumb_stdin(command, files="-"):
    source = fileinput.input(files)
    trees_from_stdin = NewickParser().consume(source)
    output_trees = command.consume(trees_from_stdin)
    NewickFormatter(sys.stdout).consume(output_trees)
    source.close()

def complex_plumb(command, files="-"):
    source = fileinput.input(files)
    trees_from_stdin = ComplexNewickParser().consume(source)
    output_trees = command.consume(trees_from_stdin)
    NewickFormatter(sys.stdout).consume(output_trees)
    source.close()

def plumb_strings(command, files="-"):
    source = fileinput.input(files)
    trees_from_stdin = NewickParser().consume(source)
    output_trees = command.consume(trees_from_stdin)
    StringFormatter(sys.stdout).consume(output_trees)
    source.close()

def plumb_list(command, files="-"):
    source = fileinput.input(files)
    trees_from_stdin = NewickParser().consume(source)
    output_lists = command.consume(trees_from_stdin)
    ListPerLineFormatter(sys.stdout).consume(output_lists)
    source.close()

def plumb_null(command, files="-"):
    source = fileinput.input(files)
    trees_from_stdin = NewickParser().consume(source)
    output_trees = command.consume(trees_from_stdin)
    # Silently pull trees through the pipeline
    for t in output_trees:
        pass
    source.close()

