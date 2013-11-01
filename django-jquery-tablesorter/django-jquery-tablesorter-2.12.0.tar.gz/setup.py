from setuptools import setup

setup(
    name='django-jquery-tablesorter',
    version='2.12.0',
    url='https://github.com/mikebryant/django-jquery-tablesorter',
    description='Django package for the tablesorter plugin.',
    author='Christian Bach',
    maintainer='Mike Bryant',
    maintainer_email='mike@mikebryant.me.uk',
    license='GPL',
    keywords=['django', 'jquery', 'staticfiles'],
    platforms='any',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
    packages=['jquery_tablesorter'],
    install_requires=['django-jquery >= 1.2.6',],
    include_package_data=True,
)
