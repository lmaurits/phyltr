from phyltr.heart import get_obj

def build_pipeline(string, source):
    components = string.split("|")
    for n, args in enumerate(components):
        command_obj = get_obj(args)
        if n==0:
            generator = command_obj.consume(source)
        else:
            generator = command_obj.consume(generator)
    return generator

