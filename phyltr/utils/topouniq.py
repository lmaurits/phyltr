def are_same_topology(t1, t2):
    return t1.robinson_foulds(t2)[0] == 0.0
