from setuptools import setup, find_packages
import sparkle
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

README = read('README.md')


setup(
    name = "django-sparkle-1.5",
    version = sparkle.__version__,
    description = 'Django-sparkle is a Django application to make it easy to publish updates for your mac application using sparkle (intended for Django >= 1.5)',
    long_description = README,
    url = 'https://github.com/shezi/django-sparkle-1.5',
    author = 'Jason Emerick, Johannes Spielmann',
    author_email = 'jemerick@gmail.com, jps@shezi.de',
    license = 'BSD',
    zip_safe = False,
    packages = find_packages(),
    include_package_data = True,
    package_data = {
            '': ['*.xml'],
            },
    install_requires = [
        'django-absolute',
        'Markdown>2.1',
    ],
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)