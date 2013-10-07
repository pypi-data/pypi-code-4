from setuptools import setup

setup(
    name='django-jquery-tipsy',
    version='1.0.0a',
    url='https://github.com/mikebryant/django-jquery-tipsy',
    description='jQuery tipsy plugin packaged in a django app to speed up new applications and deployment.',
    author='Mike Bryant',
    author_email='mike@mikebryant.me.uk',
    license='MIT',
    keywords=['django', 'jquery', 'tipsy', 'staticfiles'],
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
    packages=['jquery_tipsy'],
    package_data={'jquery_tipsy': ['static/js/*.js', 'static/css/*.css']},
    install_requires=['django-jquery >= 1.6',],
)
