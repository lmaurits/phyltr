from phyltr.commands.base import PhyltrCommand

class Scale(PhyltrCommand):
    """
    Scale the branch lengths in a treestream by a constant factor.
    """
    __options__ = [
        (
            ('-s', '--scale'),
            dict(
                dest='scalefactor', type=float, default=1.0,
                help='The factor to scale by, expressed in floating point notation.')),
    ]

    def process_tree(self, t):
        for node in t.traverse():
            node.dist *= self.opts.scalefactor
        return t
