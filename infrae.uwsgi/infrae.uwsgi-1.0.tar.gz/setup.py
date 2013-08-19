from setuptools import setup, find_packages
import os

setup(
    name='infrae.uwsgi',
    version='1.0',
    description='Buildout recipe downloading, compiling and configuring uWSGI.',
    long_description = open('README.txt', 'r').read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
    author='Infrae',
    author_email='info@infrae.com',
    license='BSD',
    url='https://svn.infrae.com/buildout/infrae.uwsgi/trunk/',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    namespace_packages=['infrae',],
    include_package_data=True,
    zip_safe=False,
    classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Framework :: Buildout",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    install_requires = [
        'zc.recipe.egg',
    ],
    entry_points = {'zc.buildout': ['default = infrae.uwsgi:UWSGI']},
)
