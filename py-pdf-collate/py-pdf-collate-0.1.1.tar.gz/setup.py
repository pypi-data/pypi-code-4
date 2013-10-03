try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open("pdf_collate/version.py") as f:
    exec(f.read())

setup(
    name="py-pdf-collate",
    version=__version__,
    author="Matt Koskela",
    author_email="mattkoskela@gmail.com",
    packages=["pdf_collate"],
    url="https://github.com/mattkoskela/py-pdf-collate",
    scripts=["bin/pdf_collate"], 
    license="LICENSE",
    description="A python script that collates your PDF documents.",
    long_description=open("README.md").read(),
    install_requires=[
        "PyPDF2==1.18"
    ]
)
