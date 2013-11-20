#!/usr/bin/env python
"""
"""
import unittest
import nose
import subprocess

def test_CommandLineArguments():
    """
    Try to invoke different scripts of this pipeline, with the wrong arguments.
    Check that they always produce an error.
    """
    command_lines = [
        ("python", "src/get_gene_coords.py"),
        ("python", "src/get_gene_coords.py", "-f", "notexistingfile.txt"),
        ("python", "src/get_gene_coords.py", "--wrongoption")


    ]
    for params_set in command_lines:
        yield check_BadCommandLine, params_set


@nose.tools.raises(subprocess.CalledProcessError)
def check_BadCommandLine(params_set):
    out = subprocess.check_output(params_set,stderr=subprocess.STDOUT)

if __name__ == '__main__':
    import logging
    import doctest
    logging.basicConfig(level=logging.DEBUG)
    doctest.testmod()


