from phyltr.commands.base import PhyltrCommand
from phyltr.plumbing.sinks import StringFormatter

class Length(PhyltrCommand):
    """
    Print the length of each tree in a stream.
    """
    sink = StringFormatter

    def process_tree(self, t, _):
        return sum([n.dist for n in t.traverse()])
