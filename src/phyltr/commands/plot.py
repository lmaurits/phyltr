import os.path

try:
    from ete3 import TreeStyle, TextFace, CircleFace
except:  # pragma: no cover
    pass

from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.sinks import NullSink

colours = (
    (240,163,255),(0,117,220),(153,63,0),(76,0,92),(25,25,25),(0,92,49),(43,206,72),(255,204,153),
    (128,128,128),(148,255,181),(143,124,0),(157,204,0),(194,0,136),(0,51,128),(255,164,5),
    (255,168,187),(66,102,0),(255,0,16),(94,241,242),(0,153,143),(224,255,102),(116,10,255),
    (153,0,0),(255,255,128),(255,255,0),(255,80,5),(0,255,255))
colours = ['#%02x%02x%02x' % c for c in colours]

def get_colour_set(n):
    if n <= len(colours):
        return colours[0:n]

def ultrametric(node): # pragma: no cover
    node.img_style["vt_line_width"]=3
    node.img_style["hz_line_width"]=3
    if node.is_leaf():
        node.img_style["size"]=5
    else:
        node.img_style["size"]=0

class Plot(PhyltrCommand):
    """
    Plot each tree in a treestream graphically.
    """
    __options__ = [
        (
            ('-a', '--attribute'),
            dict(
                dest="attribute", default=None,
                help="The name of an attribute to colour leaves by")),
        (
            ('-d', '--dpi'),
            dict(
                type=int, default=300,
                help="Paper resolution (dots per square inch) to use if saving to a file, with "
                     "height and/or width specified in non-pixel units")),
        (
            ('-H', '--height'),
            dict(
                type=int, dest="height", default=None,
                help="Height of image if saving to a file. Units set by -u.")),
        (
            ('-l', '--label'),
            dict(
                default="name",
                help="Specify the name of an attribute with which to label leaves")),
        (
            ('-m', '--multiple'),
            dict(
                default=False, action="store_true",
                help="If specified, each tree in the treestream will be plotted, otherwise only "
                     "the first will be.")),
        (
            ('-s', '--no-support'),
            dict(
                default=False, action="store_true",
                help="Don't show branch support")),
        (
            ('-o', '--output'),
            dict(
                default=None,
                help="Filename to save plot to. If not specified, ETE's interactive viewer will "
                     "be launched.")),
        (
            ('-u', '--units'),
            dict(
                default="px", choices=['px', 'mm', 'in'],
                help='Units for --height and/or --width settings. "px" for pixels, '
                     '"mm" for milimetres or "in" for inches.')),
        (
            ('-w', '--width'),
            dict(
                type=int, dest="width", default=None,
                help="Width of image if saving to a file. Units set by -u.")),
    ]

    sink = NullSink

    def __init__(self, dummy=False, **kw):
        PhyltrCommand.__init__(self, **kw)
        self.dummy = dummy

        if not self.dummy:  # pragma: no cover
            # Setup TreeStyle
            self.ts = TreeStyle()
            self.ts.show_scale = False
            self.ts.show_branch_support = not self.opts.no_support
            self.ts.show_leaf_name = False

    def process_tree(self, t, n):
        # Add faces
        if self.opts.attribute:
            values = set([getattr(l, self.opts.attribute) for l in t.get_leaves()])
            colours = get_colour_set(len(values))
            colour_map = dict(zip(values, colours))
            for l in t.iter_leaves():
                mycolour = colour_map[getattr(l,self.opts.attribute)]
                if not self.dummy:  # pragma: no cover
                    l.add_face(CircleFace(radius=10,color=mycolour, style="sphere"), 0)

        # Apply labels
        if not self.dummy:  # pragma: no cover
            for l in t.iter_leaves():
                l.add_face(TextFace(getattr(l, self.opts.label)), 1)

        # Plot or save
        if self.opts.output:
            kw = {}
            if self.opts.height or self.opts.width:
                kw["h"] = self.opts.height
                kw["w"] = self.opts.width
                kw["units"] = self.opts.units
                kw["dpi"] = self.opts.dpi
            if self.opts.multiple:
                base, ext = os.path.splitext(self.opts.output)
                filename = base + ("_%06d" % (n)) + ext
            else:
                filename = self.opts.output
            if not self.dummy:
                t.render(filename, ultrametric, tree_style=self.ts, **kw)
        else: # pragma: no cover
            if not self.dummy:
                t.show(ultrametric, tree_style=self.ts)

        if self.opts.multiple:
            return None
        else:
            raise StopIteration
