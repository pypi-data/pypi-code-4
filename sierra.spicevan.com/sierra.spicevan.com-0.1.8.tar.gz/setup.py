import os

from setuptools import setup, find_packages
version='0.1.8'
name='sierra.spicevan.com'
here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
scripts = [
    'scripts/prod_deamon_start.sh',
]
requires = [
    'pyramid',
    'pyramid_debugtoolbar',
    'waitress',
    ]
classifiers = [ "Programming Language :: Python",
                "Framework :: Pyramid",
                "Topic :: Internet :: WWW/HTTP",
                "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
            ]
setup(
    name=name,
    version=version,
    description=name,
    long_description=README + '\n\n' + CHANGES,
    classifiers=classifiers,
    author='Fenton Travers',
    author_email='fenton.travers@gmail.com',
    url='sierra.spicevan.com',
    keywords='web pyramid pylons',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=requires,
    scripts = scripts,
    test_suite="sierra",
    entry_points="""\
      [paste.app_factory]
      main = sierra:main
      """,
      )
