import os
from setuptools import setup

setup(
    name='pywizard-server',
    version='0.4.20',
    packages=[
        'pwserver',
        'pwmanager',
        'pwmanager.nodes',
    ],

    package_data={
        'pwmanager': [
            'static/pwmanager/css/*'
            'static/pwmanager/js/app/*'
            'static/pwmanager/js/lib/*'
            'static/pwmanager/js/app.map',
            'static/pwmanager/js/app.js',
        ],
        'pwserver': [
            'templates/*'
        ],
        'pwmanager.nodes': [
            'templates/*'
        ]
    },

    url='',
    license='MIT',
    author='Alex Rudakov',
    author_email='ribozz@gmail.com',
    description='Server for pywizard.',
    long_description=open('README.md').read(),
    scripts=['scripts/pywizard-server'],
    install_requires=[
        'django',
        # 'django-grappelli',
        'django-suit',
        'tornado',
        'pywizard',
        'PyYaml',
        'pyzmq',
    ]
)
