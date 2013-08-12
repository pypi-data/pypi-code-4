from setuptools import setup

setup(
    name="QuickSite",
    version='0.1.1',
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
    url="https://bitbucket.org/russellhay/quicksite",
    description="A minimal-featured static site generator",
    license="OSI Attribution Assurance License",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: Attribution Assurance License",
        "Programming Language :: Python :: 2",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
    ]
)