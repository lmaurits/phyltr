import fileinput
import os
import re
import tempfile

import ete3

_BEAST_ANNOTATION_REGEX = "([a-zA-Z0-9_ \-]*?):(\[&.*?\])([0-9\.]+)([Ee])?(\-)?([0-9])*"
_BEAST_ANNOTATION_REGEX_2 = "([a-zA-Z0-9_ \-]*?)(\[&.*?\]):([0-9\.]+)([Ee])?(\-)?([0-9])*"
regex1 = re.compile(_BEAST_ANNOTATION_REGEX)
regex2 = re.compile(_BEAST_ANNOTATION_REGEX_2)

#FIXME We should be deleting and starting a new temp file for each tree file
# otherwise we're going to have problems if file 2 is shorter than file 1

class ComplexNewickParser:

    def __init__(self, burnin=0, subsample=1):
        self.burnin = burnin
        self.subsample = subsample
        self.n = 0
       
        if self.burnin:
            self.fp = tempfile.NamedTemporaryFile(mode="w+", delete=False)

    def consume(self, stream):

        self.isNexus = False
        self.firstline = False   # Actually tracks whether a line is the first NON-BLANK line in a file
        for line in stream:
            if fileinput.isfirstline():
                self.firstline = True
                # If this is the first line of a file, and we've already seen trees.
                # then this is the second or subsequent file.  Before proceeding,
                # we should handle the temp file full of tree strings read from
                # the first file
                if self.burnin and self.n > 0:
                    for t in self.yield_from_tempfile():
                        yield t

            # Skip blank lines
            if not line.strip():
                continue
           
            # Handle Nexus stuff
            cont = self.handle_nexus_stuff(line)
            if cont:
                continue

            # Try to find a likely tree on this line and extract it
            if self.detect_tree(line):
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
                    if not t:
                        continue
                    self.nexify_tree(t)
                    yield t
                self.n += 1

        if self.burnin:
            for t in self.yield_from_tempfile():
                yield t
            self.fp.close()
            os.unlink(self.fp.name)

    def handle_nexus_stuff(self, line):
        """
        Return value is whether or not this line needs to be processed further.
        """
        # Detect Nexus file format by checking first line
        if self.firstline:
            self.firstline = False
            if line.strip() == "#NEXUS":
                self.isNexus = True
                self.inTranslate = False
                self.nexus_trans = {}
                return True
            else:
                self.isNexus = False
                return False

        if not self.isNexus:
            return False

        # Detect beginning of Nexus translate block
        if "translate" in line.lower():
            self.inTranslate = True
            return True

        # Handle Nexus translate block
        if self.inTranslate:
            # Detect ending of translate block...
            if line.strip() == ";":
                self.inTranslate = False
            # ...or handle a line of translate block
            else:
                if line.strip().endswith(";"):
                    line = line[:-1]
                    self.inTranslate = False
                index, name = line.strip().split()
                if name.endswith(","):
                    name = name[:-1]
                self.nexus_trans[index] = name
            return True

        return False

    def nexify_tree(self, t):
        # Apply translations from leaves up, since usually only leaves are
        # labelled so checking nodes near the root is a waste of time.
        if self.isNexus and self.nexus_trans:
            translated = 0
            to_translate = len(self.nexus_trans)
            for node in t.traverse("postorder"):
                if node.name and node.name in self.nexus_trans:
                    node.name = self.nexus_trans[node.name]
                    translated += 1
                    if translated == to_translate:
                        break
        return t

    def detect_tree(self, line):
        if self.isNexus:
            return line.strip().startswith("tree")
        else:
            return (    ")" in line and
                        ";" in line and
                        line.count("(") == line.count(")")
                )

    def yield_from_tempfile(self):

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
                if not t:
                    continue
                self.nexify_tree(t)
                n += 1
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

