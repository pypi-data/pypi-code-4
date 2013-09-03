from distutils.core import setup

setup(
    name='django-mongo-cache',
    version='0.1',
    packages=['mongo_cache'],
    url='https://github.com/okuznetsov/django-mongo-cache',
    license='MIT',
    author='Karol Sikora @ Laboratorium.EE',
    author_email='karol.sikora@laboratorium.ee',
    description='Cache backend for django, using MongoDB and gevent connection pool',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ]
)
