from ez_setup import use_setuptools
from Cython.Distutils import build_ext
use_setuptools()

from setuptools import setup
from setuptools import Extension

setup(name="bioa",
        version="1.24",
        description="Library for viral diversity estimation and identification using next-gen sequencing data.",
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: BSD License",
            "Topic :: Scientific/Engineering :: Bio-Informatics",
            ],
        keywords="viral virus quasispecies bioinformatics next-generation sequencing",
        url="http://alan.cs.gsu.edu/vira",
        download_url="http://alan.cs.gsu.edu/vira/download",
        author="Nicholas Mancuso et al.",
        author_email="nick.mancuso@gmail.com",
        license="BSD",
        packages=[
            "bioa",
            "bioa.algorithms",
            "bioa.classes",
            "bioa.io",
            "bioa.util"],
        cmdclass = {"build_ext": build_ext},
        ext_modules=[Extension("bioa.util.metric",
                        ["bioa/util/metric.c"],
                        libraries=[],
                        include_dirs=["./bioa", "./bioa/util/"])
                    ],
        package_data={
            "bioa": ["tests/*.py"],
            "bioa.algorithms": ["tests/*.py"],
            "bioa.classes": ["tests/*.py"],
            "bioa.io": ["tests/*.py"],
            "bioa.util": ["tests/*.py"]},
        include_package_data=True,
        install_requires=[
            "pysam",
            "biopython",
            "networkx",
            "scipy",
            "numpy",
            "Cython"],
        test_suite="nose.collector",
        tests_require=["nose"],
        scripts=["bin/vira"],
        zip_safe=False)
