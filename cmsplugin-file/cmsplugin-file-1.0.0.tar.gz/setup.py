from setuptools import setup, find_packages

version = '1.0.0'

setup(
    name='cmsplugin-file',
    version=version,
    description='File plugin for django-cms, fixes issues with native file plugin with External Media Storage (e.g. S3)',
    author='Pratik Vyas',
    author_email='pratik.vyas@changer.nl',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[],
)