# coding=utf-8
from distutils.core import setup

setup(
    name='AnyValid',
    version='1.0.0',
    author='Martin Thorsen Ranang',
    author_email='mtr@ranang.org',
    packages=['any_valid', 'test'],
    scripts=[],
    url='https://github.com/mtr/AnyValid',
    description='Library that eases partial matching of objects.',
    long_description=open('README.md').read(),
    install_requires=[
        "formencode >= 1.2.0",
    ],
    classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Testing',
          ],
)
