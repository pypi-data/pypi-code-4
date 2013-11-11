#!/usr/bin/env python

from distutils.core import setup
setup(name='dnsfailover',
        version='0.0.1',
        author='Robert Pearce',
        author_email='siology.io@gmail.com',
        url='https://github.com/robertpearce/dns-failover',
        download_url='https://pypi.python.org/pypi/dnsfailover',
        description='Simple script to update dynamic DNS zones for failvoer',
        license='MIT',
        classifiers=('Intended Audience :: System Administrators',
                     'Environment :: Console',
                     'Development Status :: 3 - Alpha',
                     'Intended Audience :: Information Technology',
                     'License :: OSI Approved :: MIT License',
                     'Operating System :: POSIX',
                     'Programming Language :: Python',
                     'Topic :: Utilities'),
#        packages=['dnsfailover'],
        requires=['dnspython'],
        scripts=['service_tester.py'],
        data_files=[('/etc/', ['failover_list'])]
      )
