from distutils.core import setup
import os
import sys

DESC = """pypolicyd-spf SPF Postfix policy server implemented in Python."""

setup(name='pypolicyd-spf',
      version='1.2',
      description=DESC,
      author='Scott Kitterman',
      author_email='scott@kitterman.com',
      url='https://launchpad.net/pypolicyd-spf',
      py_modules=['policydspfsupp', 'policydspfuser'],
      keywords = ['Postfix','spf','email'],
      scripts = ['policyd-spf'],
      data_files=[(os.path.join('share', 'man', 'man1'),
          ['policyd-spf.1']), (os.path.join('share', 'man', 'man5'),
          ['policyd-spf.conf.5']), (os.path.join('/etc', 'python-policyd-spf'),
          ['policyd-spf.conf']), (os.path.join('share', 'man', 'man5'),
          ['policyd-spf.peruser.5'])],
      classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Communications :: Email :: Mail Transport Agents',
        'Topic :: Communications :: Email :: Filters',
      ]
)

if sys.version_info < (2, 6):
    raise Exception("pypolicyd-spf requires python2.6/2.7 or python3.2 and later.")
