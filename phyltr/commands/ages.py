import fileinput
import optparse
import sys

import ete2

def run():

    # Parse options
    parser = optparse.OptionParser()
    parser.add_option('-m', '--mrca', action="store_true", dest="mrca", default=False)
    options, positional = parser.parse_args()
    
    taxa = positional[0].split(",")
    files = positional[1:] if len(positional) > 1 else []
    for line in fileinput.input(files):
        t = ete2.Tree(line)
        if options.mrca:
            mrca = t.get_common_ancestor(taxa)
            print t.get_distance(mrca)
        else:
            taxa = [t.get_leaves_by_name(name=taxon)[0] for taxon in taxa]
            dists = [t.get_distance(n) for n in taxa]
            print "\t".join(map(str,dists))

    # Done
    return 0
