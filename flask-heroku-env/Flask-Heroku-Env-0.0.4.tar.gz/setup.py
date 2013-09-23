from setuptools import setup


setup(
    name='Flask-Heroku-Env',
    version='0.0.4',
    url='https://github.com/cburmeister/flask-heroku-env',
    license='MIT',
    author='Corey Burmeister',
    author_email='cburmeister@discogs.com',
    description='Easily fetch Heroku environment variables.',
    long_description=__doc__,
    py_modules=['flask_heroku'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=['Flask'],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
