# -*- coding: utf-8 -*-
"""
``pybill.main`` is a module that contains the main program of PyBill.

Basically, this program just contains the correct run function that will be run
by the binary scripts. Currently, this run function is the
:func:`~pybill.commandline.ui.run` function from :mod:`pybill.commandline.ui`
module.

This module can be executed and just runs the run function described above.
"""
__docformat__ = "restructuredtext en"

from pybill.commandline.ui import run

if __name__ == '__main__':
    run()
