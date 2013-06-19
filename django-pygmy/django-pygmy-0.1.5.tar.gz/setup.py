from setuptools import setup, find_packages

import django_pygmy


setup(
    name='django-pygmy',
    packages=find_packages(),
    include_package_data=True,
    version=django_pygmy.__version__,
    description='',
    long_description=open('README.rst').read(),
    author=django_pygmy.__author__,
    author_email='matt.lenc@gmail.com',
    url='https://github.com/mattack108/django-pygmy/',
    install_requires=[
        "pygments>=1.6",
    ],
    zip_safe=False,
)
