import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='simple-django-contact',
    version='0.1.1',
    packages=['simple-django-contact'],
    include_package_data=True,
    license='BSD License',  # example license
    description='A simple Django app to set up a contact form',
    long_description=README,
    url='http://bryanlrobinson.com/',
    author='Bryan L. Robinson',
    author_email='bryanlrobinson@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)