"""Usage:
    phyltr taxa [<files>]

Extract the taxa names from the first tree in a stream.

OPTIONS:

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

from phyltr.commands.generic import PhyltrCommand, plumb
import phyltr.utils.phyoptparse as optparse

class Taxa(PhyltrCommand):

    def process_tree(self, t):
        names = [n.name for n in t.traverse() if n.name]
        for n in sorted(names):
            print(n)
        raise StopIteration

def run():

    # Parse options
    parser = optparse.OptionParser(__doc__)
    options, files = parser.parse_args()
    
    taxa = Taxa()
    plumb(taxa, files)
