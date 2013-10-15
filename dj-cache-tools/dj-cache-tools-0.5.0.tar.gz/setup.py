from setuptools import setup
import cache_tools

install_requires = [
    'Django>=1.3',
]

tests_require = [
    'nose',
    'coverage',
]

with open('README.rst') as readmefile:
    long_description = readmefile.read()


setup(
    name='dj-cache-tools',
    version=cache_tools.__versionstr__,
    description='Django cache tools originally developed for Ella CMS',
    long_description=long_description,
    author='Ella Development Team',
    author_email='dev@ella-cms.com',
    maintainer='Vitek Pliska',
    maintainer_email='vitek@creatiweb.cz',
    license='BSD',
    url='https://github.com/ella/django-cache-tools',

    packages=('cache_tools',),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires=install_requires,
    test_suite='nose.collector',
    tests_require=tests_require
)
