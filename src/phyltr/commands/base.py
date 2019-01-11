import fileinput
import shlex
import sys

from phyltr.plumbing.sources import NewickParser
from phyltr.plumbing.sinks import NewickFormatter
from phyltr.utils.phyltroptparse import OptionParser

class PhyltrCommand:

    parser = OptionParser("Halp!")
    source = NewickParser
    sink = NewickFormatter

    @classmethod 
    def init_from_opts(cls, options, files):
        raise NotImplementedError # pragma: no cover

    @classmethod 
    def run_as_script(cls):
        # Parse the arguments.
        # If there's an error, let optparse kill the process in its usual
        # fashion, as we should only be in run_as_script if we're genuinely
        # running from an interactive shell.
        options, files = cls.parser.parse_args(exit_on_error=True)

        # Attempt to instantiate command object
        try:
            obj = cls.init_from_opts(options, files)
        except ValueError as e:
            # Bad arguments (e.g. incompatible or incomplete)
            sys.stderr.write(str(e))
            return 1

        obj.pre_print()

        raw_source = fileinput.input(files)
        in_trees = obj.init_source().consume(raw_source)
        out_trees = obj.consume(in_trees)
        obj.init_sink(sys.stdout).consume(out_trees)
        raw_source.close()

        obj.post_print()

        return 0

    @classmethod 
    def init_from_args(cls, string):
        args = shlex.split(string)
        # Parse the arguments.
        # If there is an error, do not kill the process!  Rather, raise a
        # ValueError with some helpful message and let it bubble up to the
        # caller.
        options, files = cls.parser.parse_args(args, exit_on_error=False)
        obj = cls.init_from_opts(options, files)
        return obj

    def init_source(cls):
        return cls.source()

    def init_sink(cls, stream):
        return cls.sink(stream)

    def pre_print(self):
        pass    # pragma: no cover

    def post_print(self):
        pass    # pragma: no cover

    # The conceptual heart of phyltr...

    def consume(self, stream):
        for tree in stream:
            try:
                res = self.process_tree(tree)
                if res is not None:
                    yield res
            except StopIteration:
                if hasattr(stream, 'close'):
                    stream.close()
                break
        for tree in self.postprocess():
            yield tree

    def process_tree(self, t):
        return t    # pragma: no cover

    def postprocess(self):
        return []
