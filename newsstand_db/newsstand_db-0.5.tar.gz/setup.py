from setuptools import setup

def readme():
    with open('README') as f:
        return f.read()

setup(name='newsstand_db',
      version='0.5',
      description="Create, search and analyze a DB with your Apple's newsstand app information",
      long_description=readme(),
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python :: 2.7',
        'Topic :: Office/Business :: Financial',
      ],
      keywords='apple newsstand ios analytics database db',
      url='https://github.com/jorgeblanco/newsstand_db',
      author='Jorge Blanco',
      author_email='py@jorgeblan.co',
      license='GPLv2',
      packages=['newsstand_db'],
      install_requires=[
#           'os','time','pysqlite',
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
#       scripts=['bin/dummy'],
      entry_points={
          'console_scripts': ['newsstanddb-create=newsstand_db.cmd:newsstanddb_create',
                              'newsstanddb-import=newsstand_db.cmd:newsstanddb_import',
                              'newsstanddb-update=newsstand_db.cmd:newsstanddb_autoupdate',
                              'newsstanddb-getdbfile=newsstand_db.cmd:newsstanddb_getdbfile',
                              'newsstanddb-setdbfile=newsstand_db.cmd:newsstanddb_setdbfile',
                              'newsstanddb-stats=newsstand_db.cmd:newsstanddb_getstats',
                              'newsstanddb-addproduct=newsstand_db.cmd:newsstanddb_addproduct',],
      },
      include_package_data=True,
      zip_safe=False)