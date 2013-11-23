from distutils.core import setup

setup(
    name='django-ftp-deploy',
    version='1.1.0',
    author='Lukasz Pakula',
    author_email='lukaszpakula.pl@gmail.com',
    packages=[
        'ftp_deploy', 
        'ftp_deploy.migrations',
        'ftp_deploy.tests',
        'ftp_deploy.utils',
        'ftp_deploy.server',
        # 'ftp_deploy.server.static.ftp_deploy.font.FontAwesome',
        # 'ftp_deploy.server.static.ftp_deploy.js',
        # 'ftp_deploy.server.template.ftp_deploy',
        # 'ftp_deploy.server.template.ftp_deploy.email',
        # 'ftp_deploy.server.template.ftp_deploy.log',
        # 'ftp_deploy.server.template.ftp_deploy.service',
    ],
    include_package_data=True,
    url='http://bitbucket.org/lpakula/django-ftp-deploy',
    license='LICENSE.txt',
    description='Auto FTP deployment for django.',
    long_description=open('README.rst').read(),
    install_requires=[
        "Django >= 1.5",
        "pycurl == 7.19.0.1",
        "certifi == 0.0.8",
        "django-braces == 1.2.1",
        "django-crispy-forms==1.4.0"
    ],
)