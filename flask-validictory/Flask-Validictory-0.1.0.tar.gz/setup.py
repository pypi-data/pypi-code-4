"""
Flask-Validictory
-------------

Simple integration between Flask and Validictory.
"""
import os

from setuptools import setup

module_path = os.path.join(os.path.dirname(__file__), 'flask_validictory.py')
version_line = [line for line in open(module_path)
                if line.startswith('__version_info__')][0]

__version__ = '.'.join(eval(version_line.split('__version_info__ = ')[-1]))

setup(
    name='Flask-Validictory',
    version=__version__,
    url='https://github.com/inner-loop/flask-validictory/',
    license='MIT',
    author='Mark Angrish',
    author_email='mark.angrish@innerloop.io',
    description='Simple integration between Flask and Validictory.',
    long_description=__doc__,
    py_modules=['flask_validictory'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask>=0.10.1', 'validictory>=0.9.1'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)