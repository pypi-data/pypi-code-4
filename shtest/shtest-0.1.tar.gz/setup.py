from distribute_setup import use_setuptools
use_setuptools()
import shtest
from setuptools import setup

setup(
    name='shtest',
    version=shtest.__VERSION__,
    description='''Test runner run executable as tests''',
    author="Thasso Griebel",
    author_email='thasso.griebel@gmail.com',
    url='https://github.com/thasso/shtest',
    license="BSD",
    py_modules=['shtest'],
    long_description='''\
    shtest is a test runner that can un executable scripts and other executable
    files as tests and collect and report the results. Test results can be
    written as JUnit compatible XML output.
    ''',
    install_requires=["argparse"],
    entry_points={
        "console_scripts": [
            'sh.test = shtest:main'
        ]
    }
)
