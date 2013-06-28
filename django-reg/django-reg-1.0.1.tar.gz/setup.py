from setuptools import setup
import os

from registration import get_version


# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk('registration'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        prefix = dirpath[13:] # Strip "registration/" or "registration\"
        for f in filenames:
            data_files.append(os.path.join(prefix, f))


setup(name='django-reg',
      version=get_version().replace(' ', '-'),
      description='An extensible user-registration application for Django',
      long_description=open("README").read(),
      author='Daniel Greenfeld (fork author)',
      author_email='pydanny@gmail.com',
      url='http://www.bitbucket.org/pydanny/django-registration/',
      package_dir={'registration': 'registration'},
      packages=packages,
      package_data={'registration': data_files},
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 3.3',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: Utilities'],
      )
