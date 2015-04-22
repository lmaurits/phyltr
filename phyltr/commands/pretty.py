import fileinput
import optparse

import ete2

def run():
    # Parse options
    parser = optparse.OptionParser()
    parser.add_option('-c', '--compress', action="store_true", dest="compress", default=False)
    options, files = parser.parse_args()

    # Read trees
    for line in fileinput.input(files):
        t = ete2.Tree(line)

        # Add support to interior nodes
        for node in t.traverse():
            if node.name == "NoName":
                node.name = "%.2f" % node.support

        # Collapse high probability clades
        if options.compress:
            dead_nodes = []
            for node in t.traverse("preorder"):
                if node in dead_nodes or node.is_leaf():
                    continue
                desc = node.get_descendants()
                desc.append(node)
                if all([n.support >=0.9 for n in desc]):
                    dead_nodes.extend(desc)
                    node.name = "(%.2f) %s" % (n.support, "+".join(sorted([l.name for l in node.get_leaves()])))
                    for child in node.get_children():
                        child.detach()
        print t.get_ascii()

    return 0
