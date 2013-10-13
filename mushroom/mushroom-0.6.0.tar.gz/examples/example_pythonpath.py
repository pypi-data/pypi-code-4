# This file adds the mushroom project root to the PYTHONPATH
# making it possible to run the examples directly from the
# checked out mushroom repository without having to install
# it first.

import os
import sys

EXAMPLES_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(EXAMPLES_DIR)

os.sys.path[1:1] = [PROJECT_ROOT]
