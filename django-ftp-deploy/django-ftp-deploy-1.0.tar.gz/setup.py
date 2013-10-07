from distutils.core import setup

setup(
    name='django-ftp-deploy',
    version='1.0',
    author='Lukasz Pakula',
    author_email='lukaszpakula.pl@gmail.com',
    packages=['ftp_deploy', 'ftp_deploy.migrations'],
    url='http://pypi.python.org/pypi/django-ftp-deploy/',
    license='LICENSE.txt',
    description='Auto FTP deployment for django.',
    long_description=open('README.rst').read(),
    install_requires=[
        "Django >= 1.4",
		"pycurl == 7.19.0.1"
		"certifi == 0.0.8",
    ],
)