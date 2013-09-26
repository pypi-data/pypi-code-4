from setuptools import setup

# build-essential libffi-dev python-setuptools python-dev libevent-dev libgraphviz-dev
# easy_install pip
# pip install virtualenv

setup(
    name = 'Fanery',
    version = '0.1.3',
    author = 'Marco Caramma',
    author_email = 'marco@globalsoftwaresecurity.com',
    packages = [
        'fanery',
        'tests',
        ],
    url = 'http://pypi.python.org/pypi/Fanery/',
    license = 'BSD',
    description = 'Application development framework',
    long_description = open('README.txt').read(),
    install_requires = [
        'python-dateutil',
        'memory_profiler',
        'line_profiler',
        'profilehooks',
        'pprofile',
	    'linesman',
        'objgraph',
        'psutil',
        'numpy',
        'webob',
        'ujson',
        ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: POSIX :: BSD',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
