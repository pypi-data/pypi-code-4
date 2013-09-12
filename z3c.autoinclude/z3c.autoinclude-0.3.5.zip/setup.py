from setuptools import setup, find_packages

__version__ = '0.3.5'

setup(
    name='z3c.autoinclude',
    version=__version__,
    description="Automatically include ZCML",
    long_description=(open('README.rst').read() + "\n" +
                      open('CHANGES.rst').read()),
    classifiers=[
        "Framework :: Zope3",
        "Programming Language :: Python",
    ],
    keywords='',
    author='Zope Foundation and Contributors',
    author_email='zope-dev@zope.org',
    url='http://pypi.python.org/pypi/z3c.autoinclude',
    license='ZPL',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['z3c'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'zope.dottedname',
        'zope.interface',
        'zope.configuration',
        'zope.schema',
        'zc.buildout',
    ],
    extras_require={'test': ['zc.buildout', 'zope.testing']},
    entry_points="""
    [console_scripts]
    autoinclude-test = z3c.autoinclude.tests.tests:interactive_testing_env
    """,
)
