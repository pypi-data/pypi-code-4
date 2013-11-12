from os.path import join, dirname
from setuptools import setup


def readme_text(file_name):
    return open(join(dirname(__file__), file_name)).read()


setup(
    name='mercuro',
    version='0.1.0',
    author='Brian Cline',
    author_email='brian.cline@gmail.com',
    description=('A simple daemon that listens for syslog events and '
                 'forwards them to a Riemann server.'),
    license = 'Apache',
    keywords = 'syslog rsyslog riemann logging',
    url = 'https://github.com/briancline/mercuro',
    packages=['mercuro'],
    long_description=readme_text('README.md'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
)
