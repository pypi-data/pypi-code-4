from setuptools import setup
import os.path

setup(
    name = 'mailchimp',
    version = '2.0.1',
    author = 'MailChimp Devs',
    author_email = 'api@mailchimp.com',
    description = 'A CLI client and Python API library for the MailChimp email platform.',
    long_description = open(os.path.join(os.path.dirname(__file__), 'README')).read(),
    license = 'MIT',
    keywords = 'mailchimp email api',
    url = 'https://bitbucket.org/mailchimp/mailchimp-api-python/',
    scripts = ['scripts/mailchimp'],
    py_modules = ['mailchimp'],
    install_requires = ['requests >= 0.13.2', 'docopt == 0.4.0'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Communications :: Email'
    ]
)
