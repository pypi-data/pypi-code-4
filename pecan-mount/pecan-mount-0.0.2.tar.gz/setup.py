from setuptools import setup, find_packages
import os
import re

readme = os.path.join(os.path.dirname(__file__), 'README.rst')
LONG_DESCRIPTION = open(readme).read()

module_file = open("pecan_mount/__init__.py").read()
metadata = dict(re.findall("__([a-z]+)__\s*=\s*'([^']+)'", module_file))

setup(
    name='pecan-mount',
    version=metadata['version'],
    description="Mount Pecan apps",
    long_description=LONG_DESCRIPTION,
    install_requires = ['pecan'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ],
    keywords='mount, pecan, wsgi',
    packages=find_packages(),
    author='Alfredo Deza',
    author_email='alfredo [at] deza.pe',
    license='MIT',
    zip_safe=False,
    # At some point we ought to add this
    entry_points="""
    [pecan.extension]
    mount = pecan_mount
    """
)
