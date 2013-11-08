from setuptools import setup, find_packages

setup(
    name='cmsplugin-price',
    version='1.0.5',
    description='Extendable price form plugin for Django CMS with spam protection and i18n',
    long_description=open('README.rst').read(),
    author='Vinit Kumar',
    author_email='vinit.kumar@changer.nl.com',
    url='http://github.com/vinitkumar/cmsplugin-price',
    packages=find_packages(),
    keywords='price form django cms django-cms spam protection email',
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
