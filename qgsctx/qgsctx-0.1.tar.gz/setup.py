from distutils.core import setup
classifiers = ['Development Status :: 3 - Alpha',
'Environment :: X11 Applications :: Qt',
'Intended Audience :: Developers',
'License :: OSI Approved :: BSD License',
'Operating System :: OS Independent',
'Topic :: Scientific/Engineering :: GIS']

setup(name='qgsctx', py_modules=['qgsctx'], url='http://bitbucket.org/kurhan/qgsctx',
description='Helps launching QGIS plugins as standalone applications',
author='Milosz Piglas', author_email='milosz@archeocs.com', version='0.1',
classifiers=classifiers, long_description='Initialize data providers and map layers '+\
'for QGIS plugins which are launched as standalone applications')