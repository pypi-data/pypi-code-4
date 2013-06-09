# -*- coding: utf-8 -*-
#from ez_setup import use_setuptools
#use_setuptools(version='0.6c7')

import os
import glob
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

if not "HOME" in os.environ and  "HOMEPATH" in os.environ:
    os.environ.setdefault("HOME", os.environ.get("HOMEPATH", ""))
    print "Initializing HOME environment variable to '%s'" % os.environ["HOME"]

setup(
        name = "pyojo",
        version = "0.0.2",
        description= " Web framework to create Dojo apps.",
        author = "Txema Vicente",
        author_email = "txema@nabla.net",
        license = "BSD",
        keywords = "WSGI dojo",
        url = "http://www.pyojo.com",
        #packages=['pyojo'],
        packages = find_packages('src'),
        package_dir={'':'src'},
        package_data = {'pyojo': ['config.ini',
                                  'js/lib/js/*.js',
                                  'server/www/*.*',
                                  'server/www/pyojo/js/*.js',
                                  'server/www/static/css/*.*',
                                  'server/www/static/img/*.*',
                                  'server/www/static/js/*.*',
                                  'server/www/static/js/shjs/*.js',
                                  'server/www/static/js/shjs/css/*.css',
                                  'server/www/static/js/shjs/lang/*.js'
                                  ]},
        long_description=read('README.txt'),
        classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "License :: OSI Approved :: BSD License"],
        #data_files=files,
        entry_points={
            'console_scripts':['pyojo-server = pyojo.server.wsgi:main',
                               'pyojo-tests = pyojo.tests:main',
                           ]
                  },
)
