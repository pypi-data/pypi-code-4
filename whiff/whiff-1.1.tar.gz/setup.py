from distutils.core import setup
import sys
import glob

long_description = """
WHIFF (WSGI HTTP Integrated Filesystem Frames) is a suite of tools
to help developers create web applications using the Python/WSGI
standard server interface.

WHIFF is intended to make it easier to create, deploy, and maintain
large and complex Python based WSGI Web applications.  

The primary tools which reduce complexity are
an infrastructure for managing web application name spaces,
a configuration template language for wiring named components into an application, and
an applications programmer interface for accessing named components from Python and javascript modules. 
"""

if sys.version<"2.3":
    raise ValueError, "requires python 2.3 or better"

whiff_scripts = glob.glob("scripts/*.py")

setup(name="whiff",
      version="1.1",
      description="WHIFF: WSGI HTTP Integrated Filesystem Frames",
      long_description=long_description,
      author="Aaron Watters",
      author_email="aaron_watters@sourceforge.net",
      url="http://whiff.sourceforge.net/",
      license="BSD",
      keywords="wsgi http web cgi javascript",
      packages=[
    'whiff',
    'whiff.rdjson',
    'whiff.resources',
    'whiff.middleware',
    'whiff.middleware.png',
    'whiff.middleware.ofc',
    'whiff.middleware.mako',
    'whiff.middleware.repoze',
    'whiff.middleware.jquery',
    'whiff.middleware.jquery.js',
    'whiff.middleware.jquery.css',
    'whiff.middleware.jquery.css.smoothness',
    'whiff.middleware.jquery.css.smoothness.images',
    'whiff.middleware.jquery.css.ui-lightness',
    'whiff.middleware.jquery.css.ui-lightness.images',
    'whiff.servers',
    'whiff.servers.fsCSI',
    'whiff.servers.fsCSI',
    'whiff.servers.fsCSI.fsCSIroot',
    ],
      #package_dir={'whiff.middleware': 'whiff/middleware'},
      package_data={
         "whiff.middleware": ["data/*.bdf", "data/*.jpg", "*.whiff"],
         'whiff.servers.fsCSI.fsCSIroot': ["*.whiff"],
         "whiff.middleware.png": ["*.whiff"],
         "whiff.middleware.ofc": ["*.js", "*.swf"],
         "whiff.middleware.jquery": ["*.whiff"],
         "whiff.middleware.jquery.js": ["*.js"],
         "whiff.middleware.jquery.css.smoothness": ["*.css"],
         "whiff.middleware.jquery.css.smoothness.images": ["*.png"],
         "whiff.middleware.jquery.css.ui-lightness": ["*.css"],
         "whiff.middleware.jquery.css.ui-lightness.images": ["*.png"],
         },
      scripts = whiff_scripts,
      classifiers = [
        "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: Apache Software License",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 2.5",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
            "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
            "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
            "Topic :: Text Processing :: Markup :: HTML",
            ],
           )

