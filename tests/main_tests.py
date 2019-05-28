import pytest

from phyltr import main


def test_help(capsys):
    for cmd in main._COMMANDS:
        with pytest.raises(SystemExit) as e:
            main.run_command(cmd + ' --help')
            assert e.status == 0
