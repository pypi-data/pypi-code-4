import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-ui-permissions',
    version='0.1',
    author='Piotr Olejarz',
    author_email='vadwook@hotmail.com',
    url='http://bitbucket.org/vadwook/django-ui-permissions/',
    packages=['ui_permissions', 'ui_permissions.descriptor', 'ui_permissions.templatetags',
              'ui_permissions.descriptor.components', 'ui_permissions.tests'],
    license='LICENSE.txt',
    description='Django module that helps manage UI elements using permissions',
    long_description=README,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ]
)