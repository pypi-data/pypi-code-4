# coding: UTF-8
from distutils.core import setup
from os import path

readme = path.join(path.dirname(__file__), 'README')
if path.exists(readme):
    with open(readme) as fd:
        long_description = fd.read()

else:
    long_description = None


setup(
    name             = 'Flask-ReportableError',
    version          = '0.4.0',
    license          = 'BSD',
    platforms        = 'any',
    url              = 'https://github.com/Montegasppa/Flask-ReportableError',
    download_url     = 'https://github.com/Montegasppa/Flask-ReportableError/archive/next_release.zip',
    py_modules       = ['flask_reportable_error'],
    author           = 'Rodrigo Cacilhας',
    author_email     = 'batalema@cacilhas.info',
    description      = 'handle errors that can be reported to the web client',
    long_description = long_description,
    install_requires = ['Flask>=0.10.1'],
    classifiers      = [
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
