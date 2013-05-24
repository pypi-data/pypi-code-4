import os
from setuptools import setup, find_packages
import multilingual_orgs as app


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''


setup(
    name="django-multilingual-orgs",
    version=app.__version__,
    description=read('DESCRIPTION'),
    long_description=read('README.rst'),
    license='The MIT License',
    platforms=['OS Independent'],
    keywords='django, cms, plugin, organizations, profile, localization',
    author='Daniel Kaufhold',
    author_email='daniel.kaufhold@bitmazk.com',
    url="https://github.com/bitmazk/django-multilingual-orgs",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=1.4.3',
        'South',
        'django-libs',
        'django-cms',
        'django-filer',
        'simple-translation',
        'Pillow',
        'django-people',
        'django-localized-names'
    ],
    tests_require=[
        'fabric',
        'factory_boy<2.0.0',
        'django-nose',
        'coverage',
        'django-coverage',
        'mock',
        'flake8',
        'ipdb',
    ],
    test_suite='multilingual_orgs.tests.runtests.runtests',
)
