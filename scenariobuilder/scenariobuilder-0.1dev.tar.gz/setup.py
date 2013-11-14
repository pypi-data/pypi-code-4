from distutils.core import setup

setup(
    name='scenariobuilder',
    version='0.1dev',
    author='Michael Chapman',
    author_email='woppin@gmail.com',
    packages=['scenariobuilder'],
    scripts=['bin/sb'],
    license='LICENSE.txt',
    long_description=open('README').read(),
    setup_requires=[
        "python-novaclient",
        "python-neutronclient",
        "PyYaml>=3.10",
        "jinja2>=2.7.1"
    ],
    
)
