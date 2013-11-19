import os
from setuptools import setup

# lockdown
# Module to encrypt local Python code using AES-256.
# Decompresses code into the Lockdown object.

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "lockdown",
    version = "0.4.0",
    author = "Johan Nestaas",
    author_email = "johannestaas@gmail.com",
    description = ("An un-audited security tool to encrypt Python code."),
    license = "BSD",
    keywords = "crypto cryptography security source code",
    url = "https://bitbucket.org/johannestaas/lockdown",
    packages=['lockdown'],
    long_description=read('README'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Utilities',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development',
        'Topic :: System :: Software Distribution',
    ],
    install_requires=[
        'pycrypto',
    ],
    entry_points = {
        'console_scripts': [
            'lockdown = lockdown.bin:lockdown',
        ],
    },
)
