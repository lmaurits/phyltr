"""Usage:
    phyltr plot [<options>] [<files>]

Plot each tree in a treestream graphically.

OPTIONS:

    -a, --attribute
        Specify the name of an attribute to colour leaves by

    -d, --dpi
        Paper resolution (dots per square inch) to use if saving to a file,
        with height and/or width specified in non-pixel units

    -H, --height
        Height of image if saving to a file.  Units set by -u.

    -l, --label
        Specify the name of an attribute with which to label leaves

    -m, --multiple
        If specified, each tree in the treestream will be plotted, otherwise
        only the first will be.

    -o, --output
        Filename to save plot to.  If not specified, ETE's interactive viewer
        will be launched.

    -u, --units
        Units for --height and/or --width settings.  Should be "px" for pixels
        (the default), "mm" for milimetres or "in" for inches.

    -w, --width
        Width of image if saving to a file.  Units set by -u.

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import os.path

try:
    from ete3 import TreeStyle, TextFace, CircleFace
except:
    pass

from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.sinks import NullSink
from phyltr.utils.phyltroptparse import OptionParser

colours = ((240,163,255),(0,117,220),(153,63,0),(76,0,92),(25,25,25),(0,92,49),(43,206,72),(255,204,153),(128,128,128),(148,255,181),(143,124,0),(157,204,0),(194,0,136),(0,51,128),(255,164,5),(255,168,187),(66,102,0),(255,0,16),(94,241,242),(0,153,143),(224,255,102),(116,10,255),(153,0,0),(255,255,128),(255,255,0),(255,80,5),(0,255,255))
colours = ['#%02x%02x%02x' % c for c in colours]

def get_colour_set(n):
    if n <= len(colours):
        return colours[0:n]

def ultrametric(node): # pragma: no cover
    node.img_style["vt_line_width"]=0
    if node.is_leaf():
        node.img_style["size"]=5
    else:
        node.img_style["size"]=0

class Plot(PhyltrCommand):

    sink = NullSink

    parser = OptionParser(__doc__, prog="phyltr plot")
    parser.add_option('-a', '--attribute', dest="attribute", default=None)
    parser.add_option('-d', '--dpi', type="int", default=None)
    parser.add_option('-H', '--height', type="int", dest="height", default=None)
    parser.add_option('-l', '--label', default="name")
    parser.add_option('-m', '--multiple', default=False, action="store_true")
    parser.add_option('-o', '--output', default=None)
    parser.add_option('-u', '--units', default="px")
    parser.add_option('-w', '--width', type="int", dest="width", default=None)

    def __init__(self, label="name", attribute=None, output=None, multiple=False, width=None, height=None, units="px", dpi=300, dummy=False):

        self.label = label
        self.attribute = attribute
        self.output = output
        self.multiple = multiple
        self.width = width
        self.height = height
        self.units = units
        self.dpi = dpi
        self.n = 0

        self.dummy = dummy

        if not self.dummy:
            # Setup TreeStyle
            self.ts = TreeStyle()
            self.ts.show_scale = False
            self.ts.show_branch_support = True

    @classmethod
    def init_from_opts(cls, options, files):
        plot = Plot(options.label, options.attribute, options.output, options.multiple, options.width, options.height, options.units, options.dpi)
        return plot

    def process_tree(self, t):

        # Add faces
        if self.attribute:
            values = set([getattr(l, self.attribute) for l in t.get_leaves()])
            colours = get_colour_set(len(values))
            colour_map = dict(zip(values, colours))
            for l in t.iter_leaves():
                mycolour = colour_map[getattr(l,self.attribute)]
                if not self.dummy:
                    l.add_face(CircleFace(radius=10,color=mycolour, style="sphere"), 0)

        # Apply labels
        if not self.dummy:
            for l in t.iter_leaves():
                l.add_face(TextFace(getattr(l, self.label)), 1)

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
                filename = base + ("_%06d" % (self.n+1)) + ext
            else:
                filename = self.output
            if not self.dummy:
                t.render(filename, ultrametric, tree_style=self.ts, **kw)
        else: # pragma: no cover
            if not self.dummy:
                t.show(ultrametric, tree_style=self.ts)

        self.n += 1

        if self.multiple:
            return None
        else:
            raise StopIteration
