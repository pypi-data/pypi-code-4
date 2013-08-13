from os.path import join, dirname
from setuptools import setup

try:
    f = open(join(dirname(__file__), 'README.rst'))
    long_description = f.read().strip()
    f.close()
except IOError:
    long_description = None

setup(
    name='django-sencha',
    version='1.1.4',
    include_package_data=True,
    url="http://cellarosi@bitbucket.org/cellarosi/django-sencha",
    description='Django project contain static files about extjs 4.2',
    long_description=long_description,
    author='Marco Cellarosi',
    author_email='cellarosi@gmail.com',
    license='MIT',
    keywords='django sencha extjs staticfiles'.split(),
    platforms='any',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
    packages=['sencha'],    
)