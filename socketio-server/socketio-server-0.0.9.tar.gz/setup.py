from setuptools import setup, find_packages

setup(
    name='socketio-server',
    version='0.0.9',
    author='John Leith',
    author_email='leith.john@gmail.com',
    packages=find_packages(),
    url='http://pypi.python.org/pypi/socketio-server/',
    description='Quick and dirty socketio server for django',
    long_description=open('README.rst').read(),
    install_requires=[
        "Django>=1.4,<=1.5",
        "gevent-socketio>=0.3.4"
    ],
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst', '*.md'],
    },
    include_package_data=True,
    zip_safe=False,
)
