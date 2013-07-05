from setuptools import setup
import os


def read(filename):
    """Open a file and return its contents."""
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()


setup(
    name='easyemail',
    version='0.1.3',
    description="Simple lib abstracting email sending with smtplib.",
    long_description=read('README.md'),
    url='http://github.com/niktto/easyemail/',
    license=read('LICENSE'),
    author=u'Marek Szwalkiewicz',
    author_email='marek@szwalkiewicz.waw.pl',
    packages=['easyemail'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Mako==0.7.3',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)