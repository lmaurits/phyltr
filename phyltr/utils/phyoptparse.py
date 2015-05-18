from optparse import OptionParser as StdOptionParser
import sys

class OptionParser(StdOptionParser):

    def __init__(self, help_msg, *args, **kwargs):
        kwargs["add_help_option"] = False
        StdOptionParser.__init__(self, *args, **kwargs)
        self.help_msg = help_msg
        self.add_option('-h', '--help', action="store_true", dest="help", default=False)

    def parse_args(self, *args, **kwargs):
        options, files = StdOptionParser.parse_args(self, *args, **kwargs)
        if options.help:
            print self.help_msg
            sys.exit(0)

        return options, files
