
import sys
from setuptools import setup

setup_args = dict(
    name='tikatko',
    version='0.1',
    py_modules=['tikatko'],

    description="""A lightning talk timer""",
    author='Petr Viktorin',
    author_email='encukou@gmail.com',
    install_requires=['gillcup_graphics==0.2.0-alpha.1'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    entry_points={
        'console_scripts': ['tikatko = tikatko:script_entry_point'],
    },
)

if __name__ == '__main__':
    setup(**setup_args)
