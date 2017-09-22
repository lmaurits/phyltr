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
        raise NotImplementedError # pragma: no cover

    @classmethod 
    def run_as_script(cls):
        # Parse the arguments.
        # If there's an error, optparse will brutally kill us here.
        # That's not so bad here, as this codepath should only be followed
        # when we are genuinely running from a shell.
        # Things are different in init_from_args()...
        options, files = cls.parser.parse_args()

        # Explicit request for help
        if options.help:
            print(cls.help_string)
            return 0

        # Attempt to instantiate command object
        try:
            obj = cls.init_from_opts(options, files)
        except ValueError as e:
            # Bad arguments (e.g. incompatible or incomplete)
            sys.stderr.write(str(e))
            return 1

        obj.pre_print()

        raw_source = fileinput.input(files)
        in_trees = cls.source().consume(raw_source)
        out_trees = obj.consume(in_trees)
        cls.sink(sys.stdout).consume(out_trees)
        raw_source.close()

        obj.post_print()

        return 0

    @classmethod 
    def init_from_args(cls, string):
        args = shlex.split(string)
        try:
            options, files = cls.parser.parse_args(args)
        except SystemExit:
            # optparse didn't like our args and tried to brutally kill us!
            # But this code may be called from some non-shell context and we
            # would rather just throw an exception than shut everything down.
            # Ideally this exception would convey some useful information, but
            # optparse is a little badly designed in this sense and all
            # information is lost...
            raise ValueError("Error parsing arguments.")
        obj = cls.init_from_opts(options, files)
        return obj

    def pre_print(self):
        pass    # pragma: no cover

    def post_print(self):
        pass    # pragma: no cover

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
