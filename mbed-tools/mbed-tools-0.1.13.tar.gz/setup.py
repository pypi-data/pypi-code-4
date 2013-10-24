"""
This module defines the attributes of the
PyPI package for the Mbed SDK
"""

from distutils.core import setup

LICENSE = open('LICENSE').read()
DESCRIPTION = """A set of Python scripts that can be used to compile programs written on top of the `mbed framework`_. It can also be used to export mbed projects to other build systems and IDEs (uVision, IAR, makefiles).

.. _mbed framework: http://mbed.org"""
OWNER_NAMES = 'emilmont, bogdanm'
OWNER_EMAILS = 'Emilio.Monti@arm.com, Bogdan.Marinescu@arm.com'

setup(name='mbed-tools',
      version='0.1.13',
      description='Build and test system for mbed',
      long_description=DESCRIPTION,
      author=OWNER_NAMES,
      author_email=OWNER_EMAILS,
      maintainer=OWNER_NAMES,
      maintainer_email=OWNER_EMAILS,
      packages=['mbed_tools', 'mbed_tools.workspace_tools', 
          'mbed_tools.workspace_tools.data',
          'mbed_tools.workspace_tools.dev',
          'mbed_tools.workspace_tools.export',
          'mbed_tools.workspace_tools.host_tests',
          'mbed_tools.workspace_tools.toolchains'],
      package_dir={
          'mbed_tools': '',
          'mbed_tools.workspace_tools': 'workspace_tools',
          'mbed_tools.workspace_tools.data': 'workspace_tools/data',
          'mbed_tools.workspace_tools.dev': 'workspace_tools/dev',
          'mbed_tools.workspace_tools.export': 'workspace_tools/export',
          'mbed_tools.workspace_tools.host_tests': 'workspace_tools/host_tests',
          'mbed_tools.workspace_tools.toolchains': 'workspace_tools/toolchains'},
      url='https://github.com/mbedmicro/mbed',
      license=LICENSE)
