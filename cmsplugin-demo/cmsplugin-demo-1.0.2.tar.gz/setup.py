from setuptools import setup, find_packages

setup(
    name='cmsplugin-demo',
    version='1.0.2',
    description='Extendable demo form plugin for Django CMS with spam protection and i18n',
    long_description=open('README.rst').read(),
    author='Maccesch',
    author_email='maccesch@gmail.com',
    url='http://github.com/maccesch/cmsplugin-demo',
    packages=find_packages(),
    keywords='demo form django cms django-cms spam protection email',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
)
