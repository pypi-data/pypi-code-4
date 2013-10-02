import sys


__author__ = 'Tommaso Barbugli'
__copyright__ = 'Copyright 2013, Tommaso Barbugli'
__credits__ = []


__license__ = 'BSD'
__version__ = '0.5.3'
__maintainer__ = 'Tommaso Barbugli'
__email__ = 'tbarbugli@gmail.com'
__status__ = 'Production'

setup_install = any(
    'setup.py' in arg for arg in sys.argv) and 'install' in sys.argv

if not setup_install:
	from datadog import DataDogPeriodicPusher
