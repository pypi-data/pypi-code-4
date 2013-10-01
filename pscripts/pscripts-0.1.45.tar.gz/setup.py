from setuptools import setup
version='0.1.45'
name='pscripts'
scripts = [
    'scripts/python-deployment',
    'scripts/hdmi_brightness'    
]
classifiers = [
        'Programming Language :: Python :: 3.3',
    ]
setup(
    name = name,
    version = version,
    packages = [name],
    description = 'Automation Scripts for Linux',
    author='Fenton Travers',
    author_email='fenton.travers@gmail.com',
    url='www.google.com',
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description='Automates some python deployment steps',
    classifiers=classifiers,
    scripts = scripts
)
