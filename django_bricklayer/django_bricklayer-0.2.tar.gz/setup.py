import os
from distutils.core import setup
from setuptools import find_packages
VERSION = "0.2"
CLASSIFIERS = [
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Topic :: Software Development',
]
install_requires = [
    'django>=1.4.1',
]
# taken from django-registration
# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)
for dirpath, dirnames, filenames in os.walk('bricklayer'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        prefix = dirpath[12:] # Strip "admin_tools/" or "admin_tools\"
        for f in filenames:
            data_files.append(os.path.join(prefix, f))
setup(
    name="django_bricklayer",
    description="Django application providing command-lines utilities similar to Ruby on Rails 'scaffold' command.",
    version=VERSION,
    author="Luca Adalberto Vandro",
    author_email="lucavandro@gmail.com",
    url="https://github.com/Ianus/bricklayer/",
    download_url="https://github.com/Ianus/bricklayer/archive/master.zip",
    package_dir={'bricklayer': 'bricklayer'},
    packages=packages,
    package_data={'bricklayer': data_files},
    include_package_data=True,
    install_requires=install_requires,
    classifiers=CLASSIFIERS,
)