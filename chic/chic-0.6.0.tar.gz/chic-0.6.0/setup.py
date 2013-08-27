from setuptools import setup, find_packages

version = "0.6.0"

long_description = ""
try:
    long_description=file('README.md').read()
except Exception:
    pass

license = ""
try:
    license=file('LICENSE').read()
except Exception:
    pass


setup(
    name = 'chic',
    version = version,
    description = 'CHecker for Items and Components',
    author = 'Pablo Saavedra',
    author_email = 'saavedra.pablo@gmail.com',
    url = 'http://github.com/psaavedra/chic',
    packages = find_packages(),
    package_data={
    },
    scripts=[
        "tools/chic-checker",
        "tools/chic-get",
        "tools/chic-to-zabbix",
        "tools/chic-to-mosaic",
        "tools/chic-memcache",
        "tools/chic-memcache-get",
        "tools/chic-memcache-stats",
    ],
    zip_safe=False,
    install_requires=[
        "httplib2",
        "urllib3",
        "simplejson",
        "python-memcached",

    ],
    data_files=[
        ('/usr/share/doc/chic/', ['cfg/chic-checker.cfg.example']),
    #     ('/etc/init.d', ['init-script'])
    ],

    download_url= 'https://github.com/psaavedra/chic/zipball/master',
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    long_description=long_description,
    license=license,
    keywords = "python check streaming udp sources",
)
