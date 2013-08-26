import os
from setuptools import setup
from mobilvest import VERSION

f = open(os.path.join(os.path.dirname(__file__), 'README.md'))
readme = f.read()
f.close()

setup(
    name='django-mobilvest',
    version=".".join(map(str, VERSION)),
    description='This Django is a sms-sender backend for http://mobilvest.ru service',
    long_description=readme,
    author="Ilya Beda",
    author_email='ir4y.ix@gmail.com',
    url='https://bitbucket.org/ir4y/django-mobilvest',
    packages=['mobilvest'],
    include_package_data=True,
    install_requires=['setuptools'],
    zip_safe=False,
    classifiers=[
    'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
