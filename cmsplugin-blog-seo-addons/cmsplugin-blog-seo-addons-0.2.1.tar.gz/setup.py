import os
from setuptools import setup, find_packages
import cmsplugin_blog_seo_addons as app


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''


setup(
    name="cmsplugin-blog-seo-addons",
    version=app.__version__,
    description=read('DESCRIPTION'),
    long_description=read('README.rst'),
    license='The MIT License',
    platforms=['OS Independent'],
    keywords='django, blog, django-cms, app, plugin, meta, description',
    author='Daniel Kaufhold',
    author_email='daniel.kaufhold@bitmazk.com',
    url="https://github.com/bitmazk/cmsplugin-blog-seo-addons",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=1.4.3',
        'South',
        'django-cms',
        'cmsplugin-blog',
        'django-tagging-translated',
    ],
    tests_require=[
        'fabric',
        'django-libs',
        'factory-boy<2.0.0',
        'django-nose',
        'coverage',
        'django-coverage',
        'mock',
        'ipdb',
        'flake8',
        'Pillow',
    ],
    test_suite='cmsplugin_blog_seo_addons.tests.runtests.runtests',
)
