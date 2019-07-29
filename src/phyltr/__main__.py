"""Phyltr

Usage:
  phyltr <command> [<args>]

The available phyltr commands are:
{0}

All commands can be abbreviated to their first three letters, e.g. running
"phyltr col" is the same as running "phyltr collapse".

Command specific help is availble via "phyltr <command> --help".
"""

import os.path
import shlex
from signal import signal, SIGPIPE, SIG_DFL
import sys
from textwrap import shorten

# import all commands:
from phyltr.commands import *  # noqa: F401, F403
from phyltr.commands.base import PhyltrCommand

COMMANDS = {cls.__name__.lower(): cls for cls in PhyltrCommand.__subclasses__()}


def _format_command_overview():
    max_name = max(len(k) for k in COMMANDS)
    res = []
    for cmd in sorted(COMMANDS.keys()):
        res.append('  {0} {1}'.format(
            cmd.ljust(max_name), shorten(COMMANDS[cmd].__doc__, 77 - max_name)))
    return '\n'.join(res)


def _split_string(spec_string):
    spec_string = spec_string.strip()
    bits = spec_string.split(" ", 1)
    if len(bits) == 1:
        command, args = bits[0], ""
    else:
        command, args = bits
    return command, args


def _get_class(command):
    for match in COMMANDS:
        if command in (match, match[0:3]):
            return COMMANDS[match]

    raise ValueError("Command not recognised")


def _get_phyltr_obj(spec_string):
    command, args = _split_string(spec_string)
    class_ = _get_class(command)
    return class_.init_from_args(args)


def run_command(command_string=None, files=None):
    signal(SIGPIPE, SIG_DFL)

    # If fed a command string, simulate having got it from the shell
    if command_string is not None:
        sys.argv = shlex.split(command_string)
        sys.argv.insert(0, "phyltr")

    # Running 'phyltr' with no command is the same as running 'phyltr help'
    if len(sys.argv) > 1:
        command = sys.argv.pop(1)
    else:
        command = "help"

    # Check if the supplied command is one we know about
    try:
        class_ = _get_class(command)
    except ValueError:
        # If it wasn't a real command, maybe it was a request for help?
        if command in ("--help", "help", "--usage", "usage"):
            print(__doc__.format(_format_command_overview()))
            return 0
        # If not, give up and tell the user to seek help
        else:
            sys.stderr.write(
                "phyltr: '%s' is not a phyltr command.  See 'phyltr --help'.\n" % command)
            return 0

    # If we've gotten this far, we're running a real command, so let's do it!
    return class_.run_as_script(files=files)


def build_pipeline(string, source):
    components = string.split("|")
    for n, args in enumerate(components):
        command_obj = _get_phyltr_obj(args)
        if n == 0:
            if isinstance(source, str) and os.path.exists(source):
                # If source is a filename, feed it to the command's default
                # Source
                fp = open(source, "r")
                source = command_obj.init_source().consume(fp)
            generator = command_obj.consume(source)
        else:
            # Subsequent components in the pipline should use their proceeding
            # component as a source
            generator = command_obj.consume(generator)
    # We don't attach a sink as presumably in the use case for this function
    # "the code is the sink"
    return generator


if __name__ == '__main__':  # pragma: no cover
    run_command()
