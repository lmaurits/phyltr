import fileinput
import optparse
import shlex
import sys

from phyltr.plumbing.sources import NewickParser
from phyltr.plumbing.sinks import NewickFormatter

class PhyltrCommand:

    help_string = "Halp"
    parser = optparse.OptionParser(add_help_option = False)
    parser.add_option('-h', '--help', action="store_true", dest="help", default=False)
    source = NewickParser
    sink = NewickFormatter

    @classmethod 
    def init_from_opts(cls, options, files):
        raise NotImplementedError

    @classmethod 
    def run_as_script(cls):
        try:
            options, files = cls.parser.parse_args()
        except SystemExit:
            # Bad commandline arguments (i.e. non-existent arg given)
            print("Help!")
            return 0

        if options.help:
            # Explicit request for help
            print(cls.help_string)
            return 0

        try:
            obj = cls.init_from_opts(options, files)
        except:
            # Bad arguments (e.g. incompatible or incomplete)
            print("Oh no!")
            return 1

        raw_source = fileinput.input(files)
        in_trees = cls.source().consume(raw_source)
        out_trees = obj.consume(in_trees)
        cls.sink(sys.stdout).consume(out_trees)
        raw_source.close()
        return 0

    @classmethod 
    def init_from_args(cls, string):
        args = shlex.split(string)
        options, files = cls.parser.parse_args(args)
        obj = cls.init_from_opts(options, files)
        return obj

    # The conceptual heart of phyltr...

    def consume(self, stream):
        for tree in stream:
            try:
                res = self.process_tree(tree)
                if res:
                    yield res
            except StopIteration:
                stream.close()
                break
        for tree in self.postprocess():
            yield tree

    def process_tree(self, t):
        return t    # pragma: no cover

    def postprocess(self):
        return []
