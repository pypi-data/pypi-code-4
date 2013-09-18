import os
from setuptools import setup, find_packages


def read_file(filename):
    path = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(path, filename)
    try:
        return open(filepath).read()
    except IOError:
        return ''


setup(
    name='django-zen',
    version='0.1.8',
    author='Vitaliy Korobkin',
    author_email='root@digitaldemiurge.me',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/DigitalDemiurge/django-zen.git',
    install_requires=[
        'Django>=1.4',
        'django-mptt>=0.5',
        'feincms>=1.7.4',
        'django-wysiwyg-redactor==0.3.5',
    ],
    license='MIT license',
    description='Zen-Lightweight Django CMS',
    classifiers=[
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
    ],
    long_description=read_file('README.md'),
    test_suite="runtests.runtests",
    zip_safe=False,
)
