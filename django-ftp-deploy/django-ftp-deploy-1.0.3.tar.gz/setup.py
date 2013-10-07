from distutils.core import setup

setup(
    name='django-ftp-deploy',
    version='1.0.3',
    author='Lukasz Pakula',
    author_email='lukaszpakula.pl@gmail.com',
    packages=['ftp_deploy', 'ftp_deploy.migrations'],
    url='http://bitbucket.org/lpakula/django-ftp-deploy',
    license='LICENSE.txt',
   	keywords="django, ftp, deploy", 
    description='Auto FTP deployment for django.',
    long_description=open('README.rst').read(),
    install_requires=[
        "Django >= 1.4",
		"pycurl == 7.19.0.1"
		"certifi == 0.0.8",
    ],
)