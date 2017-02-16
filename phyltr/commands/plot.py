"""Usage:
    phyltr plot [<options>] [<files>]

Plot each tree in a treestream graphically.

OPTIONS:

    -a, --attribute
        Specify the name of an attribute to colour leaves by

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import fileinput
import os.path

import ete2

import phyltr.utils.phyoptparse as optparse

colours = ((240,163,255),(0,117,220),(153,63,0),(76,0,92),(25,25,25),(0,92,49),(43,206,72),(255,204,153),(128,128,128),(148,255,181),(143,124,0),(157,204,0),(194,0,136),(0,51,128),(255,164,5),(255,168,187),(66,102,0),(255,0,16),(94,241,242),(0,153,143),(224,255,102),(116,10,255),(153,0,0),(255,255,128),(255,255,0),(255,80,5),(0,255,255))
colours = ['#%02x%02x%02x' % c for c in colours]

def get_colour_set(n):
    if n <= len(colours):
        return colours[0:n]

def ultrametric(node):
    node.img_style["vt_line_width"]=0
    if node.is_leaf():
        node.img_style["size"]=5
    else:
        node.img_style["size"]=0
        
def run():
    # Parse options
    parser = optparse.OptionParser(__doc__)
    parser.add_option('-a', '--attribute', dest="attribute", default=None)
    parser.add_option('-d', '--dpi', type="int", default=None)
    parser.add_option('-H', '--height', type="int", dest="h", default=None)
    parser.add_option('-l', '--label', default="name")
    parser.add_option('-m', '--multiple', default=False, action="store_true")
    parser.add_option('-o', '--output', default=None)
    parser.add_option('-u', '--units', default="px")
    parser.add_option('-w', '--width', type="int", dest="w", default=None)
    options, files = parser.parse_args()

    # Setup TreeStyle
    ts = ete2.TreeStyle()
    ts.show_scale = False
    ts.show_branch_support = True

    # Read trees
    for n, line in enumerate(fileinput.input(files)):
        t = ete2.Tree(line)

        # Add faces
        if options.attribute:
            values = set([getattr(l, options.attribute) for l in t.get_leaves()])
            colours = get_colour_set(len(values))
            colour_map = dict(zip(values, colours))
            for l in t.iter_leaves():
                mycolour = colour_map[getattr(l,options.attribute)]
                l.add_face(ete2.CircleFace(radius=10,color=mycolour, style="sphere"), 0)
        for l in t.iter_leaves():
            l.add_face(ete2.TextFace(getattr(l, options.label)), 1)

        # Plot or save
        if options.output:
            kw = {}
            if options.h or options.w:
                for o in ("h","w","units","dpi"):
                    if getattr(options, o):
                        kw[o] = getattr(options, o)
            if options.multiple:
                base, ext = os.path.splitext(options.output)
                filename = base + ("_%06d" % (n+1)) + ext
            else:
                filename = options.output
            t.render(filename, ultrametric, tree_style=ts, **kw)
        else:
            t.show(ultrametric, tree_style=ts)

        if not options.multiple:
            return 0

    return 0
