from setuptools import setup, find_packages

setup(
    name='cmsplugin-question',
    version='1.0.2',
    description='Question form contact plugin',
    long_description=open('README.rst').read(),
    author='Vinit Kumar',
    author_email='vinit.Kumar@changer.nl',
    url='http://github.com/vinitkumar/cmsplugin-question',
    packages=find_packages(),
    keywords='Question form django cms django-cms spam protection email',
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
