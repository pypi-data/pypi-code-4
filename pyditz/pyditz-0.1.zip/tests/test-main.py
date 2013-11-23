"""
Main console test.
"""

import os
from ditz.console import main


def test_run():
    "Test main application"

    os.chdir("example")
    main(["-v", "todo"])
    os.chdir("..")


if __name__ == "__main__":
    test_run()
