from setuptools import setup, find_packages

setup(name='setuptools-epydoc',
    version='0.1',
    description='Epydoc API documentation generation command for pylint',
    long_description='''
    Provides a setuptools command that uses the epydoc tool to generate API
    documentation for python projects.
    ''',
    classifiers=[
        'Topic :: Documentation',
        'Framework :: Setuptools Plugin',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Topic :: Software Development :: Documentation',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='epydoc setuptools command',
    author='Johannes Wienke',
    author_email='languitar@semipol.de',
    url='https://github.com/languitar/setuptools-epydoc',
    license='MPL',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=['epydoc'],
    entry_points={
        'distutils.commands': [
            'epydoc = setuptools_epydoc:EpydocCommand',
        ]
    }
)
