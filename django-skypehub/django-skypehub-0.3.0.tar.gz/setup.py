import os

from setuptools import setup, find_packages


setup(
    name='django-skypehub',
    version='0.3.0',
    description='Skype API bridge for Django',
    author='Shinya Okano',
    author_email='tokibito@gmail.com',
    url='http://bitbucket.org/tokibito/django-skypehub/',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    license='BSD',
    keywords='django skype',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
    ],
    install_requires=[
        'Django',
        'Skype4Py',
    ],
    zip_safe=False,
)
