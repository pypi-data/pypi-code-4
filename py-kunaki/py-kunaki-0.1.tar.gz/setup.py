import os
from distutils.core import setup


project_name = 'kunaki'
long_description = open('README.rst').read()

# Idea from django-registration setup.py
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk(project_name):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'):
            del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        prefix = dirpath[(len(project_name) + 1):]
        for f in filenames:
            data_files.append(os.path.join(prefix, f))

setup(
    name='py-kunaki',
    version=__import__(project_name).__version__,
    package_dir={project_name: project_name},
    packages=packages,
    package_data={project_name: data_files},
    description='Python module to interface with the Kunaki.com XML API',
    author='Netlandish Inc.',
    author_email='geeks@netlandish.com',
    license='BSD License',
    url='https://bitbucket.org/netlandish/py-kunaki/',
    long_description=long_description,
    platforms=['any'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Environment :: Web Environment',
    ],
)
