from setuptools import setup, find_packages

setup(
    name='socketio-server',
    version='0.0.2',
    author='John Leith',
    author_email='leith.john@gmail.com',
    packages=find_packages(),
    url='http://pypi.python.org/pypi/socketio-server/',
    description='Quick and dirty socketio server for django',
    long_description=open('README.md').read(),
    install_requires=[
        "Django == 1.4",
        "gevent-socketio"
    ],
    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst', '*.md'],
    },

)
