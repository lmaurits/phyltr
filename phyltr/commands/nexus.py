"""Usage:
    phyltr nexus [<files>]

Convert a treestream to a file in the NEXUS forma.  The NEXUS output is printed to stdout, where it can be redirected to a file.

OPTIONS:

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import fileinput

import ete2

import phyltr.utils.phyoptparse as optparse

def run():

    # Parse options
    parser = optparse.OptionParser(__doc__)
    options, files = parser.parse_args()

    # Read trees
    first = True
    for count, line in enumerate(fileinput.input(files),1):
        t = ete2.Tree(line)
        leaves = t.get_leaves()
        # If first tree, get names
        if first:
            names = sorted([l.name for l in leaves])
            print_middle(names)
            first = False
        for l in leaves:
            if l.name in names:
                l.name = str(names.index(l.name)+1)

        # Print tree line
        print "TREE tree_%d = %s" % (count, t.write())
    
    print_footer()

    # Done
    return 0

def print_header():
    print "#NEXUS\n"

def print_middle(names):
    print "Begin taxa;"
    print "\tDimensions ntax=%d;" % len(names)
    print "\t\tTaxlabels"
    for name in names:
        print "\t\t\t%s" % name 
    print "\t\t\t;"
    print "End;"

    print "Begin trees;"
    print "\tTranslate"
    for count, name in enumerate(names,1):
        print "\t\t%d %s," % (count, name)
    print "\t\t;"

def print_footer():
    print "End;"
