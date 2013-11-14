#!/usr/bin/env python
import subprocess
subprocess.call(["make", "--directory=../docs/", "html"])
