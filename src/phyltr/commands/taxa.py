from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.sinks import ListPerLineFormatter

class Taxa(PhyltrCommand):
    """
    Extract the taxa names from the first tree in a stream.
    """
    sink = ListPerLineFormatter

    def __init__(self, **kw):
        PhyltrCommand.__init__(self, **kw)
        self.done = False

    def process_tree(self, t):
        if self.done:
            raise StopIteration
        else:
            self.done = True
            return sorted([n.name for n in t.traverse() if n.name])
