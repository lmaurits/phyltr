"""Usage:
    phyltr taxa [<files>]

Extract the taxa names from the first tree in a stream.

OPTIONS:

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import phyltr.utils.phyoptparse as optparse
from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.helpers import plumb_list

class Taxa(PhyltrCommand):

    def __init__(self):
        self.done = False

    def process_tree(self, t):
        if self.done:
            raise StopIteration
        else:
            names = [n.name for n in t.traverse() if n.name]
            self.done = True
            return sorted(names)

def run():

    # Parse options
    parser = optparse.OptionParser(__doc__)
    options, files = parser.parse_args()
    
    taxa = Taxa()
    plumb_list(taxa, files)
