"""
Main console program.
"""

import sys
from commands import DitzCmd


def main():
    cmd = DitzCmd(search=True, usecache=True, autosave=True)

    if len(sys.argv) == 1:
        try:
            cmd.cmdloop()
        except KeyboardInterrupt:
            pass
    else:
        try:
            command = " ".join(sys.argv[1:])
            retval = cmd.onecmd(command)
            sys.exit(0 if retval else 1)
        except Exception as msg:
            sys.exit("%s: error: %s" % (sys.argv[0], str(msg)))

if __name__ == "__main__":
    main()
