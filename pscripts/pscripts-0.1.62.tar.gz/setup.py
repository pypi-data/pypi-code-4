from setuptools import setup
version='0.1.62'
name='pscripts'
scripts = [
    'scripts/python-deployment',
    'scripts/hdmi_brightness',
    'scripts/update_external_ip',
]
classifiers = [
        'Programming Language :: Python :: 3.3',
    ]
install_requires=[
    'setuptools',
    'SimpleDaemon >= 1.3.0',
    'PyYAML >= 3.10',
    'pidfile >= 0.1.0',
    ]
Data_Files = [('/etc/external_ip_updater/', ['urls.yaml','config.conf'])]
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
    scripts = scripts,
    data_files=Data_Files,
)
