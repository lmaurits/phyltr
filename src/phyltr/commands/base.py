import fileinput
import shlex
import sys
import argparse

from phyltr.plumbing.sources import NewickParser
from phyltr.plumbing.sinks import NewickFormatter


class PhyltrCommand(object):

    source = NewickParser
    sink = NewickFormatter
    __options__ = []  # Derived classes should add parser arguments here.
    __opt_dests = []  # When initializing an ArgumentParser, we store the argument dests here.

    def __init__(self, _opts=None, **kw):
        """
        Command options can be initialized in two ways:

        1. By passing an `argparse.Namespace` object as `_opts`.
        2. By passing values for individual options a keyword arguments.
        """
        if _opts:
            self.opts = _opts
        else:
            # We initialize the options with the default values of the ArgumentParser:
            p = self.parser()
            defaults = {d: p.get_default(d) for d in self.__opt_dests}
            defaults.update(kw)
            self.opts = argparse.Namespace(**defaults)

    @classmethod
    def parser(cls):
        """
        Assembles a pre-subcommand ArgumentParser, with the command-specific options added.

        :return: ArgumentParser
        """
        cls.__opt_dests = []
        res = argparse.ArgumentParser(
            description=cls.__doc__.strip(),
            prog='phyltr {0}'.format(cls.__name__.lower()),
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        for args, kw in cls.__options__:
            cls.__opt_dests.append(res.add_argument(*args, **kw).dest)
        return res

    @classmethod
    def run_as_script(cls, files=None):
        # Parse the arguments.
        # If there's an error, let arparse kill the process in its usual
        # fashion, as we should only be in `run_as_script` if we're genuinely
        # running from an interactive shell.
        options = cls.parser().parse_args()

        # Attempt to instantiate command object
        try:
            obj = cls(_opts=options)
        except (SystemExit, ValueError, argparse.ArgumentError) as e:
            # Bad arguments (e.g. incompatible or incomplete)
            sys.stderr.write(str(e))
            return 1

        obj.pre_print()

        raw_source = fileinput.input(getattr(options, 'files', []) + (files or []))
        in_trees = obj.init_source().consume(raw_source)
        out_trees = obj.consume(in_trees)
        obj.init_sink(sys.stdout).consume(out_trees)
        raw_source.close()

        obj.post_print()

        return 0

    @classmethod 
    def init_from_args(cls, string):
        # Parse the arguments.
        # If there is an error, do not kill the process!  Rather, raise a
        # ValueError with some helpful message and let it bubble up to the
        # caller.
        return cls(_opts=cls.parser().parse_args(shlex.split(string)))

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
        i = 0
        for i, tree in enumerate(stream, start=1):
            try:
                res = self.process_tree(tree, i)
                if res is not None:
                    yield res
            except StopIteration:
                if hasattr(stream, 'close'):
                    stream.close()
                break
        for tree in self.postprocess(i):
            yield tree

    def process_tree(self, t, n):
        # The default tree processing is just passing them through:
        return t

    def postprocess(self, tree_count):
        return []
