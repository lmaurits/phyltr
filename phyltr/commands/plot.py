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

import os.path

import ete3

import phyltr.utils.phyoptparse as optparse
from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.helpers import plumb_strings

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

class Plot(PhyltrCommand):

    def __init__(self, label="name", attribute=None, output=None, multiple=False, width=None, height=None, units="px", dpi=None):

        self.label = label
        self.attribute = attribute
        self.output = output
        self.multiple = multiple
        self.width = width
        self.height = height
        self.units = units
        self.dpi = dpi
        self.n = 0

        # Setup TreeStyle
        self.ts = ete3.TreeStyle()
        self.ts.show_scale = False
        self.ts.show_branch_support = True

    def process_tree(self, t):

        # Add faces
        if self.attribute:
            values = set([getattr(l, self.attribute) for l in t.get_leaves()])
            colours = get_colour_set(len(values))
            colour_map = dict(zip(values, colours))
            for l in t.iter_leaves():
                mycolour = colour_map[getattr(l,self.attribute)]
                l.add_face(ete3.CircleFace(radius=10,color=mycolour, style="sphere"), 0)

        # Apply labels
        for l in t.iter_leaves():
            l.add_face(ete3.TextFace(getattr(l, self.label)), 1)

        # Plot or save
        if self.output:
            kw = {}
            if self.height or self.width:
                kw["h"] = self.height
                kw["w"] = self.width
                kw["units"] = self.units
                kw["dpi"] = self.dpi
            if self.multiple:
                base, ext = os.path.splitext(self.output)
                filename = base + ("_%06d" % (n+1)) + ext
            else:
                filename = self.output
            t.render(filename, ultrametric, tree_style=self.ts, **kw)
        else:
            t.show(ultrametric, tree_style=self.ts)

        self.n += 1

        if self.multiple:
            return None
        else:
            raise StopIteration

def run():
    
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

    plot = Plot(options.label, options.attribute, options.output, options.multiple, options.width, options.height, options.units, options.dpi)
    plumb_strings(plot, files)
