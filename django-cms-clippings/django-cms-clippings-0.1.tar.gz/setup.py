import os
import sys

from setuptools import setup, find_packages


def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as fp:
        return fp.read()


if 'sdist' in sys.argv:
    # clear compiled mo files before building the distribution
    walk = os.walk(os.path.join(os.getcwd(), 'clippings/locale'))
    for dirpath, dirnames, filenames in walk:
        if not filenames:
            continue
        if 'django.mo' in filenames:
            os.unlink(os.path.join(dirpath, 'django.mo'))
else:
    # compile the po files
    try:
        import django
    except ImportError:
        pass
    else:
        current_dir = os.getcwd()
        os.chdir(os.path.join(current_dir, 'clippings'))
        os.system('django-admin.py compilemessages')
        os.chdir(current_dir)


setup(
    name='django-cms-clippings',
    version='0.1',
    description='Include editable content in applications integrated with django-cms sites.',
    long_description=read("README.rst"),
    author='Stuart MacKay',
    author_email='smackay@flagstonesoftware.com',
    url='http://pypi.python.org/pypi/django-cms-clippings/',
    license='GPL',
    packages=find_packages(),
    keywords='django, cms, editable, content, plugins',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Natural Language :: English",
        "Framework :: Django",
    ],
    install_requires=[
        'django-cms',
    ],
)
