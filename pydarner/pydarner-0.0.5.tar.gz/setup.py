
from setuptools import setup, find_packages

setup(
    name='pydarner',
    version='0.0.5',
    description='A python darner client',
    long_description='A python darner client based on the python-memcached library.',
    keywords='queues darner memcached',
    author='Ebot Tabi',
    author_email='ebottabi@siqueries.com',
    maintainer='Ebot Tabi',
    maintainer_email='ebottabi@siqueries.com',
    url='https://github.com/siqueries/pydarner',
    download_url='https://github.com/siqueries/pydarner/tarball/0.0.5',
    license='BSD',
    packages=find_packages(exclude=['ez_setup', 'tests', 'tests.*']),
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'python-memcached>=1.45',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python',
    ],
)
