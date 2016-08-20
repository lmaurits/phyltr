import dendropy

def read_tree(string):
    t = dendropy.Tree.get_from_string(line,schema="newick")

def write_tree(t):
    print t.as_string(schema="newick", suppress_rooting=True,suppress_annotations=False).strip()
