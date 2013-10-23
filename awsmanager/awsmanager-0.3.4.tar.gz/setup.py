#!/usr/bin/env python

from distutils.core import setup
setup(name='awsmanager',
        version='0.3.4',
        author='Robert Pearce',
        author_email='siology.io@gmail.com',
        url='https://github.com/robertpearce/aws-manager',
        download_url='https://pypi.python.org/pypi/awsmanager',
        description='Simple boto wrapper script',
        license='MIT', 
        classifiers=('Intended Audience :: System Administrators',
                     'Environment :: Console',
                     'Development Status :: 3 - Alpha',
                     'Intended Audience :: Information Technology',
                     'License :: OSI Approved :: MIT License',
                     'Operating System :: POSIX',
                     'Programming Language :: Python',
                     'Topic :: Utilities'),
        packages=['awsmanager'],
        requires=['boto'],
        scripts=['awsm'],
        data_files=[('/etc/', ['aws_manager.cfg'])]
      )
