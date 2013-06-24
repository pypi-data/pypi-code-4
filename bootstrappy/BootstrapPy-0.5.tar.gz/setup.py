from setuptools import setup, find_packages
import sys, os

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

version = '0.5'

setup(name='BootstrapPy',
    version=version,
    description="A Python web framework with Twitter's Bootstrap.",
    long_description="""A Python MVC web framework that utilizes technologies like Twitter's Bootstrap, JQuery, Knockout, and SQLAlchemy. Comes with a built-in JSON API, useful database tables, and lots of example code.""",
    classifiers=['Environment :: Web Environment'],
    keywords='python web framework bootstrap sqlalchemy knockout jquery bootstrappy',
    author='Noel Morgan',
    author_email='noel@bootstrappy.org',
    url='http://www.bootstrappy.org',
    license='MPL 2.0',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "Paste>=1.7.5.1",
        "PasteScript>=1.7.5",
        "Beaker>=1.6.4",
        "FormEncode>=1.2.4",
        "Jinja2>=2.6",
        "Genshi>=0.6",
        "WebError>=0.10.3",
        "WebHelpers>=1.3",
        # "psycopg2>=2.4", # Uncomment for PostgreSQL Support
        "transaction>=1.3",
        "zope.sqlalchemy>=0.7.1",
        "Pygments>=1.5",
        "MarkupSafe>=0.15",
        "simplejson",
        "decorator>=3.4.0",
        "SQLAlchemy>=0.7.9",
        "WebOb>=0.5.1"
    ],
    setup_requires=["PasteScript>=1.7.5"],
    entry_points="""
    [paste.paster_create_template]
    BootstrapPy = bootstrappy.tmplt:BootstrapPyTemplate
    """,)
