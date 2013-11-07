from setuptools import setup

setup(
    name='stillson',
    version='0.1.1',
    author='Mortar Data',
    author_email='info@mortardata.com',
    packages=['stillson'],
    entry_points = {
        'console_scripts': [
            'stillson = stillson.stillson:main',
        ]
    },
    url='https://github.com/mortardata/stillson/',
    license='LICENSE',
    description='Tool for generating config files using a template and environment variables.',
    long_description='Tool for generating config files using a template and environment variables. https://github.com/mortardata/stillson',
    install_requires=[
        "mako >= 0.8.0",
    ],
)
