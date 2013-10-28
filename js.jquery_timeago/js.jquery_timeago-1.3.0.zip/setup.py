from setuptools import setup, find_packages
import os

# The version of the wrapped library is the starting point for the
# version number of the python package.
# In bugfix releases of the python package, add a '-' suffix and an
# incrementing integer.
# For example, a packaging bugfix release version 1.4.4 of the
# js.jquery package would be version 1.4.4-1 .

version = '1.3.0'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('js', 'jquery_timeago', 'test_jquery_timeago_plugin.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='js.jquery_timeago',
    version=version,
    description="Fanstatic packaging of jQuery timeago plugin",
    long_description=long_description,
    classifiers=[],
    keywords='',
    url='https://github.com/dnozay/js.jquery_timeago',
    author='Damien Nozay',
    author_email='damien.nozay@gmail.com',
    license='BSD',
    packages=find_packages(),namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'setuptools',
        'js.jquery'
        ],
    entry_points={
        'fanstatic.libraries': [
            'jquery_timeago_plugin = js.jquery_timeago:library',
            ],
        },
    )
