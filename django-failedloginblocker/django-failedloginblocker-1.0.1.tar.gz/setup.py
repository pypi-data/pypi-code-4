from setuptools import setup

setup(
    name='django-failedloginblocker',
    version='1.0.1',
    packages=['failedloginblocker'],
    package_data={
        '': ['*.html'],
    },
    license='BSD (3-Clause) License',
    long_description=open('README').read(),
    maintainer='mySociety',
    maintainer_email='programmers@mysociety.org',
    url='https://github.com/mysociety/django-failedloginblocker',
)
