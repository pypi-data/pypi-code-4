from setuptools import setup

setup(
    name = 'Fanery',
    version = '0.1.1',
    author = 'Marco Caramma',
    author_email = 'marco@globalsoftwaresecurity.com',
    packages = [
        'fanery',
        'fanery.dbms',
        'fanery.locales',
        'fanery.test',
        ],
    url = 'http://pypi.python.org/pypi/Fanery/',
    license = 'BSD',
    description = 'Application development framework',
    long_description = open('README.txt').read(),
    install_requires = [
        'python-dateutil',
        #'memory_profiler',
        #'line_profiler',
        #'pprofiler',
        #'objgraph',
        'psutil',
        'numpy',
        'webob',
        #'nose',
        #'rawes',
        #'netaddr',
        #'pygeoip',
        #'pycountry',
        ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
