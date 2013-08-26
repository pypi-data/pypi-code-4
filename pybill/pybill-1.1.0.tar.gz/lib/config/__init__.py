# -*- coding: utf-8 -*-
"""
``pybill.lib.config`` package contains all the code that manages the
configurations.

The only public class that should be used outside of this package is the
:class:`~pybill.lib.config.register.ConfigRegister` class that is imported and
available in the namespace of this package.
"""
__docformat__ = "restructuredtext en"

# Imports the classes that must be used from the outside.
from pybill.lib.config.register import ConfigRegister
