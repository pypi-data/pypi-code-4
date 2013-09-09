from setuptools import setup

from os import path as op
CURRENT_DIR = op.dirname(__file__)

__version__ = '0.1.6'

setup(
    name='dropbox_backup',
    version=__version__,
    scripts= ['bin/dropbox_backup'],
    packages=['dropbox_backup'],

    install_requires=open(op.join(CURRENT_DIR, 'requirements.txt')).read().splitlines(),

    author='Thomas Kliszowski',
    author_email='thomas.kliszowski@gmail.com',
    description='Create backup from your server and send them to dropbox',
    license='MIT',
    keywords='dropbox backup upload',
    url='http://dropbox-backup.org',
    long_description=open(op.join(CURRENT_DIR, 'README.rst')).read(),
    include_package_data=True,
    zip_safe=False,
)
