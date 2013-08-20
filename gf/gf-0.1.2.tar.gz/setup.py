"""Our setup script."""

import sys
from setuptools import setup

long_description_header_text = "GF: Lisp-Like generic Functions"
long_description_header_decoration = "=" * len(long_description_header_text)
long_description_header = "\n".join((
        long_description_header_decoration,
        long_description_header_text,
        long_description_header_decoration))
try:
    with open("docs/overview.rst") as readme_file:
        long_description = (long_description_header + "\n" +
                readme_file.read())
    with open("docs/acknowledgements.rst") as readme_file:
        long_description += readme_file.read()
except IOError:
    long_description = None

sys.path.insert(0, "tests")

setup(name="gf",
      version='0.1.2',
      description="A package with lisp-like generic functions.",
      long_description = long_description,
      author="Gerald Klix",
      author_email="gf@klix.ch",
      packages=['gf'],
      url="http://pypi.python.org/pypi/gf",
      zip_safe=True,
      test_suite="testgo",
      license="PSF",
      )
