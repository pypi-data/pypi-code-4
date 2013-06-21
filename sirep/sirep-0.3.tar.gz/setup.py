import os
from setuptools import setup, find_packages

try:
  readme = open(os.path.join(os.path.dirname(__file__), 'readme.rst')).read()
except:
  readme = ''

version = '0.3'

setup(
    name='sirep',
    version=version,
    description=("Simple reporting for Django admin."),
    long_description=readme,
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python",
        "Environment :: Web Environment",
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    keywords='reporting, django, admin, app, python',
    author='Artur Barseghyan',
    author_email='artur.barseghyan@gmail.com',
    url='https://bitbucket.org/barseghyanartur/sirep',
    package_dir={'':'src'},
    packages=find_packages(where='./src'),
    license='GPL 2.0/LGPL 2.1',
    #download_url='https://bitbucket.org/barseghyanartur/sirep/get/%s.tar.gz' % version,
    install_requires=['python-dateutil'],
    package_data={'': ['templates/list.html', 'templates/view.html', 'static/admin/css/sirep.css']}
)
