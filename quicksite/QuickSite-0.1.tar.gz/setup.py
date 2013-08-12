from setuptools import setup

setup(
    name="QuickSite",
    version='0.1',
    packages=[
        "quicksite",
        "configbuilder"
    ],
    entry_points = {
        'console_scripts': [
            'configbuilder = configbuilder.__main__:main',
            'quicksite = quicksite.script:main'
        ]
    },
    author="Russell Hay",
    author_email="me@russellhay.com",
    url="https://bitbucket.org/russellhay/quicksite"
)