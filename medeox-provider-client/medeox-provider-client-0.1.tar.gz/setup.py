import os
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()


setup(
    name='medeox-provider-client',
    version='0.1',
    platforms='OS Independent',
    description='A Medeox provider client library',
    long_description=README + '\n\n' + CHANGES,
    license='TODO',
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Development Status :: 5 - Production/Stable'
    ],
    keywords='medeox websockets socket.io node.js',
    author='Medeox',
    author_email='tech@doctoralia.com',
    url='https://github.com/medeox/Medeox.Provider.Python',
    install_requires=[
        'requests',
        'websocket-client',
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True)