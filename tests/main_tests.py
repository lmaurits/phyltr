import pytest

from phyltr import COMMANDS, run_command


def test_help(capsys):
    for cmd in COMMANDS:
        with pytest.raises(SystemExit) as e:
            run_command(cmd + ' --help')
            assert e.status == 0
