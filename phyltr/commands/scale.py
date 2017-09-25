"""Usage:
    phyltr scale [<options>] [<files>]

Scale the branch lengths in a treestream by a constant factor.

OPTIONS:

    -s, --scale
        The factor to scale by, expressed in floating point notation.

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

from phyltr.commands.base import PhyltrCommand
from phyltr.utils.phyltroptparse import OptionParser

class Scale(PhyltrCommand):

    parser = OptionParser(__doc__, prog="phyltr scale")
    parser.add_option('-s', '--scale', type="float", default=1.0,
                help='Scaling factor.')

    def __init__(self, scalefactor=1.0):
        self.scalefactor = scalefactor

    @classmethod 
    def init_from_opts(cls, options, files):
        scale = Scale(options.scale)
        return scale

    def process_tree(self, t):
        for node in t.traverse():
            node.dist *= self.scalefactor
        return t
