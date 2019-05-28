from os.path import dirname, basename, isfile, join
import glob

# To make it possible to find all available commands by iterating over subclasses of PhyltrCommand,
# we must make sure all modules with such subclasses are imported. With the "hack" below, this
# can be achieved with "from phyltr.commands import *"
modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [
    basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
