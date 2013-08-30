from distutils.core import setup

setup(
    name = 'matrix_keypad',
    packages = ['matrix_keypad'],
    version = '1.1.3',
    description = 'Matrix Keypad code for use with Raspberry Pi',
    author='Chris Crumpacker',
	author_email = 'chris@chriscrumpacker.com',
	url = 'http://crumpspot.blogspot.com/p/keypad-matrix-python-package.html',
	classifiers = [
		"Programming Language :: Python",
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
		"Operating System :: OS Independent",
		"Environment :: Other Environment",
		"Development Status :: 4 - Beta",
		"Intended Audience :: Developers",
		"Topic :: System :: Hardware",
		"Topic :: Software Development :: Libraries :: Python Modules",
		],
	long_description = """\
Introduction
============

Python Library for Matrix Keypads. 
Written and tested on a Model B Raspberry Pi.
Supports both a 3x4 and 4x4 keypad included

:Current Version:    v1.1.3_

:Project Page:  Project_Page_
:PyPI page:  PyPI_Page_

Author
======

:Author:	Chris Crumpacker
:Email:		chris@chriscrumpacker.com
:Web:		http://www.chriscrumpacker.com
:Blog:		http://crumpspot.blogspot.com

Prerequisites
=============

If the I2C Port expander MCP23017 or MCP23008 is being used, the Adafruit Python library for I2C and the MCP will need to be installed.

You can clone the whole library like so::

	git clone https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code.git

or the two files needed can be pulled out, Adafruit_I2C.py_ & Adafruit_MCP230xx.py_.

Install
=======

You can use the source from just downloading the files or Install it as a library via PIP::

	pip install matrix_keypad
	
After the install you will need to create links to the Adafruit I2C and MCP230xx code since they are not installed as packages.::

	sudo ln -s [path to Adafruit python cod]/AdafruitMCP230xx/*.py /usr/local/lib/python2.7/dist-packages/matrix_keypad
	
Note: you will have to change the part in the brackets and maybe the path to the where the matrix keypad package is

Files Included
==============
::

    README.txt
    LICENSE.txt
    setup.py
    matrix_keypad/
        __init__.py
        matrix_keypad_RPi_GPIO.py
        matrix_keypad_MCP230xx.py
        matrix_keypad_demo.py
        matrix_keypad_demo2.py

Usage
=====
*See the demo scripts included to see this all in action.*

To call the library select which one you intend to use and use the correct line::

    from matrix_keypad import MCP230xx

or::

    from matrix_keypad import RPi_GPIO

Then initialize and give the library a short name so it is easier to reference later. For the MCP version::
	
    kp = MCP230xx.keypad(address = 0x21, num_gpios = 8, columnCount = 4

The variables here are the I2C address, then if you are using the MCP23017 or MCP23008 you have to put the number of GPIO pin avaialable (default is 8), Then the "columnCount" is 3 for the 4x3 keypads and 4 for the 4x4 keypads.

For the standard GPIO version you only have to reference the 'column count if you want to change it to the 4x4, it defaults at the 3x4::

	kp = RPi_GPIO.keypad(ColumnCount = 4)

It is possible to just check to see if a digit is currently pressed.::

    checkKeypad = kp.getKey()
	
Or a simple function to call the keypad library and 
loop through it waiting for a digit press ::

    def digit():
        # Loop while waiting for a keypress
        digitPressed = None
        while digitPressed == None:
            digitPressed = kp.getKey()
        return digitPressed
	
Version History
===============

:v0.1.0:

	Initial Scripts

:v1.0.0:
    
	Initial package build
	
:v1.0.1_:
    
	Initial package build and push to PyPI
	
:v1.0.2_:
	
	Updating the matrix_keypad_demo2.py to demo selecting the 4x4 keypad

:v1.0.3_:
	
	Moved Version Log in README
	
	Updated README Links

:v1.0.4_:
	
	Updated References to include the PiLarm code as the inspiration for the "...demo2.py" code
	
:v1.0.5_:

	Updates to the code in both main libs to fix some indenting and other issues from coping the code from blogger to a text file.
	
	Updates to the keypad picking section for the constants to make it actually work
	
:v1.0.6_:

	Fixes to more indenting issues. :(
	
:v1.1.0_:

	Updated main libs and the demo code.
	
	Added install directions to handle the links to the adafruit code

:v1.1.1_:

    Updated ...demo.py and demo2.py to reflect new package name.

    Updated README as well

:v1.1.2_:

    Updating the README project links

    Updating the code's comments


:v1.1.3_:

    Repackage

Code References
===============

Column and Row scanning adapted from Bandono's matrixQPI_ which is wiringPi based.

matrix_keypad_demo2.py is based on some work that Jeff Highsmith had done in making his PiLarm_ that was featured on Make. 


.. --------------------------------------------------------------------------
.. Links

.. _Project_Page: http://crumpspot.blogspot.com/p/keypad-matrix-python-package.html
.. _PyPI_Page: https://pypi.python.org/pypi/matrix_keypad
.. _Adafruit_I2C.py: https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/blob/master/Adafruit_I2C/Adafruit_I2C.py
.. _Adafruit_MCP230xx.py: https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/blob/master/Adafruit_MCP230xx/Adafruit_MCP230xx.py
.. _matrixQPI: https://github.com/bandono/matrixQPi?source=cc
.. _PiLarm: http://makezine.com/video/pilarm-how-to-build-a-raspberry-pi-room-alarm/
.. _PiLarm_Code: https://github.com/BabyWrassler/PiNopticon/blob/master/keypadd.py
.. _v1.0.1: https://pypi.python.org/pypi/matrix_keypad/1.0.1
.. _v1.0.2: https://pypi.python.org/pypi/matrix_keypad/1.0.2
.. _v1.0.3: https://pypi.python.org/pypi/matrix_keypad/1.0.3
.. _v1.0.4: https://pypi.python.org/pypi/matrix_keypad/1.0.4
.. _v1.0.5: https://pypi.python.org/pypi/matrix_keypad/1.0.5
.. _v1.0.6: https://pypi.python.org/pypi/matrix_keypad/1.0.6
.. _v1.1.0: https://pypi.python.org/pypi/matrix_keypad/1.1.0
.. _v1.1.1: https://pypi.python.org/pypi/matrix_keypad/1.1.1
.. _v1.1.2: https://pypi.python.org/pypi/matrix_keypad/1.1.2
.. _v1.1.3: https://pypi.python.org/pypi/matrix_keypad/1.1.3
"""
)