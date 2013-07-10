from setuptools import setup, find_packages
import os

version = '0.9.10'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.rst')
    + '\n' +
    read('js', 'socketio', 'test_socketio.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='js.socketio',
    version=version,
    description="fanstatic socketio.",
    long_description=long_description,
    classifiers=[],
    keywords='fanstatic socketio redturtle',
    author='RedTurtle Developers',
    url='https://github.com/RedTurtle/js.socketio',
    author_email='sviluppoplone@redturtle.it',
    license='BSD',
    packages=find_packages(),
    namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'js.jquery',
        'setuptools',
        ],
    entry_points={
        'fanstatic.libraries': [
            'socketio = js.socketio:library',
            ],
        },
    )
