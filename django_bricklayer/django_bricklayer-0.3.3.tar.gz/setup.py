import os
from distutils.core import setup
from setuptools import find_packages
from distutils.core import setup
from distutils.sysconfig import get_python_lib

VERSION = "0.3.3"
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



# Warn if we are installing over top of an existing installation. This can
# cause issues where files that were deleted from a more recent Django are
# still present in site-packages. See #18115.
overlay_warning = False


def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join)
    in a platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)


EXCLUDE_FROM_PACKAGES = ['django.conf.project_template',
                         'django.conf.app_template',
                         'django.bin']


def is_package(package_name):
    for pkg in EXCLUDE_FROM_PACKAGES:
        if package_name.startswith(pkg):
            return False
    return True


# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, package_data = [], {}

root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
django_dir = 'bricklayer'

for dirpath, dirnames, filenames in os.walk(django_dir):
    # Ignore PEP 3147 cache dirs and those whose names start with '.'
    dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != '__pycache__']
    parts = fullsplit(dirpath)
    package_name = '.'.join(parts)
    if '__init__.py' in filenames and is_package(package_name):
        packages.append(package_name)
    elif filenames:
        relative_path = []
        while '.'.join(parts) not in packages:
            relative_path.append(parts.pop())
        relative_path.reverse()
        path = os.path.join(*relative_path)
        package_files = package_data.setdefault('.'.join(parts), [])
        package_files.extend([os.path.join(path, f) for f in filenames])

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
    package_data=package_data,
    install_requires=install_requires,
    classifiers=CLASSIFIERS,
)         