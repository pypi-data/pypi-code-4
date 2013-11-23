"""
Command tests.
"""

from ditz.database import DitzDB
from ditz.commands import DitzCmd
from ditz.util import read_yaml_file
from mock import Mock


def test_commands(name="example"):
    "Test commands"

    dbname = name + "-cmd"
    db = DitzDB.read(name)
    db.write(dbname)

    for test in read_yaml_file("test-cmd.yaml"):
        cmd = test.pop("cmd")
        for testcase in test.pop("tests"):
            args = testcase.pop("args") or ""
            command = cmd + " " + str(args)
            print "=== Running '%s' ===" % command
            run_command(dbname, command, **testcase)


def run_command(dbname, cmd, **kw):
    ditz = DitzCmd(dbname)

    for method in "line", "text", "choice", "yesno":
        if method in kw:
            effect = kw[method]
        else:
            effect = Exception('no %s input' % method)

        setattr(ditz, "get" + method, Mock(spec=DitzCmd, side_effect=effect))

    ditz.onecmd(cmd)


if __name__ == "__main__":
    test_commands()
