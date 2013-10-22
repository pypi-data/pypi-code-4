from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages
from distutils import log

from celerid.support import setup, Extension
import celerid, setuptools

log.set_verbosity(100)

setup(
    zip_safe = True,
	name="icc.atp",
	version="0.0.1",
	author="Evgeny Cherkashin",
	author_email="eugeneai@irnok.net",
	description="Automatic Theorem Proving wrapper for Python",

    packages=find_packages("src"),
    package_dir={"": "src"},
    namespace_packages=["icc"],

    install_requires=[
        "setuptools",
        "celerid",
    ],

	ext_modules=[
        Extension("icc.atp.atp",
                  sources=["src/icc/atp/src/atp.d"],
        )
	],

    license = "GNU GPL",
    keywords = "automatic theorem proving ATP proof first-order logics",

    long_description = """ """,

    # platform = "Os Independent.",
    # could also include long_description, download_url, classifiers, etc.

)
