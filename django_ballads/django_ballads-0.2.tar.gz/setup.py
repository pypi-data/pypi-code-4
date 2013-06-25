# Use setuptools if we can
try:
    from setuptools.core import setup
except ImportError:
    from distutils.core import setup

PACKAGE = 'django_ballads'
VERSION = '0.2'

setup(
    name=PACKAGE, version=VERSION,
    description="Django library for coordinating multi-system transactions (eg database, filesystem, remote API calls).",
    packages=[
        'django_ballads',
    ],
    license='MIT',
    author='James Aylett',
    author_email='james@tartarus.org',
    install_requires=[
        'Django>=1.5.1',
    ],
    url = 'https://github.com/jaylett/django-ballads',
    classifiers = [
        'Intended Audience :: Developers',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
    ],
)
