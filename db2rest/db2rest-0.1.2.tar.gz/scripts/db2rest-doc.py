#!/usr/bin/env python
import subprocess
from db2rest import module_doc

subprocess.call(["make", "html"], cwd=module_doc)
