from setuptools import setup, find_packages

version = '0.0.9'

setup(
    name='prdg.plone.util',
    version=version,
    description="Assorted Plone utilities.",
    long_description='\n'.join([
        open("README.txt").read(),
        open("TODO.txt").read(),
        open("HISTORY.txt").read(),
    ]),
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='plone util utilities',
    author='Rafael Oliveira',
    author_email='rafaelbco@gmail.com',
    url='',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['prdg', 'prdg.plone'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'prdg.util',
        'prdg.zope.permissions',
        'Products.validation',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
            'plone.api',
        ]
    },
    entry_points="""
    # -*- Entry points: -*-
    """,
)
