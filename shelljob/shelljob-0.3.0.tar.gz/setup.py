# shelljob setup.py
from distutils.core import setup

import pypandoc
desc = pypandoc.convert( 'README.md', 'rst' )

setup(
	name = 'shelljob',
	packages = [ 'shelljob' ],
	version = '0.3.0',
	description = 'Run multiple subprocesses asynchronous/in parallel with streamed output/non-blocking reading',
	author = 'edA-qa mort-ora-y',
	author_email = 'eda-qa@disemia.com',
	url = 'https://pypi.python.org/pypi/shelljob',
	classifiers = [
		'Development Status :: 4 - Beta',
		'Programming Language :: Python',
		'Intended Audience :: Developers',
		'Environment :: Console',
		'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
		'Operating System :: OS Independent',
		'Topic :: Terminals',
		'Topic :: System',
		'Topic :: Software Development :: Build Tools',
		],
	long_description = desc,
)
