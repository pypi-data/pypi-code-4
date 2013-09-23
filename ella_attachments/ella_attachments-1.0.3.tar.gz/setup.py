from setuptools import setup, find_packages

VERSION = (1, 0, 3)

__version__ = VERSION
__versionstr__ = '.'.join(map(str, VERSION))

install_requires = [
    'ella>=2,<4',
    'South>=0.7',
]

test_requires = [
    'nose',
    'coverage',
]

setup(
    name='ella_attachments',
    version=__versionstr__,
    description='Add attachments to Ella project',
    author='Ella Development Team',
    author_email='dev@ella-cms.com',
    license='BSD',
    url='https://github.com/ella/ella-attachments',

    packages=find_packages(
        where='.',
        exclude=('test_ella_attachments',)
    ),

    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    include_package_data=True,
    install_requires=install_requires,

    test_suite='test_ella_attachments.run_tests.run_all',
    tests_require=test_requires,
)
