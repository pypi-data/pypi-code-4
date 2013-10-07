import setuptools
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setuptools.setup(
    name="dsgrid",
    version='0.1.0',
    description="Build and Manage a Selenium Grid using Docker.",
    packages=['dsgrid'],
    author="Brady Vitrano",
    author_email="bjvitrano@gmail.com",
    license="Apache",
    keywords = "docker selenium grid firefox phantomjs",
    url="https://github.com/brady-vitrano/dsgrid",
    entry_points = {
        'console_scripts': [
            'dsgrid = dsgrid.shell:main'
        ]
    },
    install_requires = [
        'docker-py',
        'mock'
    ],
    long_description=read('README.md')
)