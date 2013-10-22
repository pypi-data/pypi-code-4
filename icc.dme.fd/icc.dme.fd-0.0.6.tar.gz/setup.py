from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages, Extension

from distutils import log

log.set_verbosity(100)

setup( zip_safe = True, name="icc.dme.fd", version="0.0.6",
       author="Evgeny Cherkashin", author_email="eugeneai@irnok.net",
       description="Dynamic Modelling Environment",

       packages=find_packages("src"),
       package_dir={"": "src"},
       namespace_packages=["icc"],

       install_requires=[
           "setuptools"
       ],

       ext_modules=[
           Extension("icc.dme.fd.DModel",
                     sources=["src/icc/dme/fd/C/DModel.c"],
                 )
       ],

       license = "GNU GPL",
       keywords = "forest resources dynamics analysis tool application",

       long_description = """ """,

       # platform = "Os Independent.",
       # could also include long_description, download_url, classifiers, etc.
)
