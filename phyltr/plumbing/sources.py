import fileinput
import os
import re
import tempfile

import ete3

_BEAST_ANNOTATION_REGEX = "([a-zA-Z0-9_ \-]*?):(\[&.*?\])([0-9\.]+)([Ee])?(\-)?([0-9])*"
_BEAST_ANNOTATION_REGEX_2 = "([a-zA-Z0-9_ \-]*?)(\[&.*?\]):([0-9\.]+)([Ee])?(\-)?([0-9])*"
regex1 = re.compile(_BEAST_ANNOTATION_REGEX)
regex2 = re.compile(_BEAST_ANNOTATION_REGEX_2)

class ComplexNewickParser:

    def __init__(self, burnin=0, subsample=1):
        self.burnin = burnin
        self.subsample = subsample
        self.n = 0
       
        self.first_file = True
        if self.burnin:
            self.fp = tempfile.NamedTemporaryFile(mode="w+", delete=False)

    def consume(self, stream):

        firstline = False
        self.isNexus = False
        for line in stream:
            if fileinput.isfirstline():
                firstline = True
                self.isNexus = False
                # If this is the first line of a file, and we've already seen trees.
                # then this is the second or subsequent file.  Before proceeding,
                # we should handle the temp file full of tree strings read from
                # the first file
                if self.burnin and self.n > 0:
                    for t in self.dump_from_backlog():
                        yield t

            # Skip blank lines
            if not line.strip():
                continue
            
            # Detect Nexus file format by checking first line
            if firstline:
                if line.strip() == "#NEXUS":
                    self.isNexus = True
                    inTranslate = False
                    self.nexus_trans = {}
                else:
                    self.isNexus = False
                firstline = False

            # Detect beginning of Nexus translate block
            if self.isNexus and "translate" in line.lower():
                inTranslate = True
                continue

            # Handle Nexus translate block
            if self.isNexus and inTranslate:
                # Detect ending of translate block...
                if line.strip() == ";":
                    inTranslate = False
                # ...or handle a line of translate block
                else:
                    if line.strip().endswith(";"):
                        line = line[:-1]
                        inTranslate = False
                    index, name = line.strip().split()
                    if name.endswith(","):
                        name = name[:-1]
                    self.nexus_trans[index] = name
                continue

            # Try to find a likely tree on this line and extract it
            if (self.isNexus and line.strip().startswith("tree") or 
               (
                    ")" in line and
                    ";" in line and
                    line.count("(") == line.count(")")
               )):
                # Smells like a tree!
                start = line.index("(")
                end = line.rindex(";") + 1
                tree_string = line[start:end]
                if self.burnin:
                    # Save for later
                    self.fp.write(tree_string+"\n")
                elif self.n % self.subsample == 0:
                    # Yield now
                    t = get_tree(tree_string)
                    if self.isNexus and self.nexus_trans:
                        for node in t.traverse():
                            if node.name and node.name in self.nexus_trans:
                                node.name = self.nexus_trans[node.name]
                    yield t
                self.n += 1

        if self.burnin:
            for t in self.dump_from_backlog():
                yield t
            self.fp.close()
            os.unlink(self.fp.name)

    def dump_from_backlog(self):

        trees_to_skip = int(round((self.burnin/100.0)*self.n))
        self.n = 0
        self.fp.seek(0)
        n = 0
        for tree_string in self.fp.readlines():
            if n < trees_to_skip:
                n += 1
                continue
            if (n-trees_to_skip) % self.subsample == 0:
                t = get_tree(tree_string)
                n += 1
                if self.isNexus and self.nexus_trans:
                    for node in t.traverse():
                        if node.name and node.name in self.nexus_trans:
                            node.name = self.nexus_trans[node.name]
                yield t
            else:
                n += 1
        self.fp.seek(0)

def get_tree(tree_string):
    # FIXME
    # Make this much more elegant
    # Also, once a successful parse is achieved, remember the strategy and avoid brute force on subsequent trees

    # Do we need regex magic?
    if "[&" in tree_string and "&&NHX" not in tree_string:
        tree_string = regex1.sub(repl, tree_string)
        if "NHX" not in tree_string:
            tree_string = regex2.sub(repl, tree_string)

    # Try to parse tree as is
    try:
        t = ete3.Tree(tree_string)
        return t
    except (ValueError,ete3.parser.newick.NewickError):
        pass

    # Try to parse tree with internal node labels
    try:
        t = ete3.Tree(tree_string, format=1)
        return t
    except (ValueError,ete3.parser.newick.NewickError):
        # That didn't fix it.  Give up
        return None

def repl(m):
    name, annotation, dist = m.groups()[0:3]
    if len(m.groups()) > 3:
        # Exponential notation
        dist += "".join([str(x) for x in m.groups()[3:] if x])
    dist = float(dist)
    if annotation:
        bits = annotation[2:-1].split(",")
        # Handle BEAST's "vector annotations"
        # (comma-separated elements inside {}s)
        # by replacing the commas with pipes
        # (this approach subject to change?)
        newbits = []
        inside = False
        for bit in bits:
            if inside:
                newbits[-1] += "|" + bit
                if "}" in bit:
                    inside = False
            else:
                newbits.append(bit)
                if "{" in bit:
                    inside = True
        annotation = "[&&NHX:%s]" % ":".join(newbits)
    return "%s:%f%s" % (name, dist, annotation)

class NewickParser:

    def consume(self, stream):
        for tree_string in stream:
            # Try to parse tree as is
            try:
                t = ete3.Tree(tree_string)
                yield t
                continue
            except (ValueError,ete3.parser.newick.NewickError):
                pass

            # Try to parse tree with internal node labels
            try:
                t = ete3.Tree(tree_string, format=1)
                yield t
            except (ValueError,ete3.parser.newick.NewickError):
                # That didn't fix it.  Give up
                continue

