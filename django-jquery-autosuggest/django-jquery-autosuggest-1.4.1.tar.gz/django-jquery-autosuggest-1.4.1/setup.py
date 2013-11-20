from setuptools import setup

setup(
    name='django-jquery-autosuggest',
    version='1.4.1',
    url='https://github.com/benbacardi/django-jquery-autosuggest',
    description='jQuery autosuggest (http://code.drewwilson.com/entry/autosuggest-jquery-plugin) packaged in a django app to speed up new applications and deployment.',
    author='Ben Cardy',
    author_email='benbacardi@gmail.com',
    license='MIT',
    keywords='django jquery autosuggest staticfiles'.split(),
    platforms='any',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
    packages=['jquery_autosuggest'],
    package_data={'jquery_autosuggest': ['static/js/*.js', 'static/css/*.css',]},
    install_requires=['django-jquery >= 1.6',],
    include_package_data=True,
)
