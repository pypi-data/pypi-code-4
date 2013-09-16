import os
from setuptools import setup
from pip.req import parse_requirements

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
INSTALL_REQUIREMENTS = [str(r.req) for r in parse_requirements("requirements/production.txt")]
TEST_REQUIREMENTS = [str(r.req) for r in parse_requirements("requirements/test.txt")]

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='zinnia-drupal',
    version='0.1.2',
    packages=['zinnia_drupal', 'zinnia_drupal.management', 'zinnia_drupal.management.commands'],
    include_package_data=True,
    license='BSD',  # example license
    description='Helper application for importing content from Drupal database into Zinnia.',
    long_description=README,
    url='https://github.com/azaghal/zinnia-drupal',
    author='Branko Majic',
    author_email='branko@majic.rs',
    install_requires=INSTALL_REQUIREMENTS,
    tests_require=TEST_REQUIREMENTS,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
