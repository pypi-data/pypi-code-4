from setuptools import setup

setup(
    name='Flask-TwitterBootstrap',
    version='0.0.4',
    packages=['flask_twitterbootstrap'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask-WTF', 'pyjade==2.0.1b'
    ],
    # supporting jinja autoescape
    dependency_links=[
        'https://github.com/vamf12/pyjade/tarball/fix_jinja_attr_escape'
        '#egg=pyjade-2.0.1b'
    ]
)
