import os
from distutils.core import setup

setup(
    name='pywizard-manager',
    version='0.4.35',
    packages=[
        'pwserver',
        'pwmanager',
        'pwmanager.nodes',
        'pwserver',
    ],

    package_data={
        'pwmanager': [
            'static/pwmanager/js/app.js',
            'static/pwmanager/js/app.map',
            'static/pwmanager/js/lib/*',
            'static/pwmanager/js/app/*',
            'static/pwmanager/css/*',
        ],
        'pwserver': [
            'templates/*'
        ],
        'pwmanager.nodes': [
            'templates/*'
        ]
    },

    url='http://pywizard.com',
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
