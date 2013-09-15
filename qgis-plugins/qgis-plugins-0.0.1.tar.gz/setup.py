import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

packages, data_files = [], []
for dirpath, dirnames, filenames in os.walk("plugins"):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
        if dirname.startswith('tests'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

print packages
print
print data_files

data_files.append('docs')

setup(
    name = "qgis-plugins",
    version = "0.0.1",
    author = "Alessandro Pasotti",
    author_email = "apasotti@gmail.com",
    description = "A django pluggable used to serve a qgis plugin repository",
    license = "GPL",
    keywords = "qgis gis plugins osgeo",
    url = "http://plugins.qgis.org",
    packages=packages,
    data_files=data_files,
    long_description=read('README'),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License (GPL)"
    ],
    install_requires=[
        "Django==1.5.4",
        "sorl-thumbnail==11.12", 
        "django-pagination==1.0.7",
        "django-ratings==0.3.7",
        "django-sorting==0.1",
        "django-taggit==0.9.3",
        "django-taggit-autosuggest==0.2",
        "django-taggit-templatetags==0.4.6dev",
        "django-templatetag-sugar==0.1",
        "rpc4django==0.2.4"
    ]
)
