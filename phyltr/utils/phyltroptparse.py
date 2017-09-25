from optparse import OptionParser as StdOptionParser
import sys

class OptionParser(StdOptionParser):

    def __init__(self, help_msg, *args, **kwargs):
        self.help_msg = help_msg
        kwargs["usage"] = help_msg
        StdOptionParser.__init__(self, *args, **kwargs)

    def format_help(self):  # pragma: no cover
        return self.help_msg

    def parse_args(self, *args, **kwargs):
        self.exit_on_error = kwargs.pop("exit_on_error", True)
        return StdOptionParser.parse_args(self, *args, **kwargs)

    def error(self, msg):
        # By default, do OptionParser's usual brutal thing
        if self.exit_on_error:
            StdOptionParser.error(self, msg) # pragma: no cover
        # But if told to, raise an exception with a useful message, rather than
        # killing the entire process.
        else:
            raise ValueError(msg)
