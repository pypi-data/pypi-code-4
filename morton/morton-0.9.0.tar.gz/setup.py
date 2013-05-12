import os

from setuptools import find_packages
from setuptools import setup

version = '0.9.0'

install_requires = [
]

tests_require = install_requires + ['Sphinx', 'docutils',
                                    'virtualenv', 'nose', 'coverage']

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.md')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.md')).read()
except IOError:
    README = CHANGES = ''

kwargs = dict(
    version=version,
    name='morton',
    description="""\
convert x,y into a Z-Order number
""",
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
      "Intended Audience :: Developers",
      "Programming Language :: Python",
      "License :: OSI Approved :: MIT License",
    ],
    install_requires=install_requires,
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    tests_require=tests_require,
    test_suite="morton.tests",
    url="http://thesoftwarestudio.com/morton/",
    author="Chris Davies",
    author_email='user@domain.com',
    entry_points="""\
    """
)

setup(**kwargs)
