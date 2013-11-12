from setuptools import setup, find_packages

long_description = """
Python client for juju-core websocket api.
"""

setup(
    name="juju-deployer",
    version="0.2.9",
    description="A tool for deploying complex stacks with juju.",
    long_description=open("README").read(),
    author="Kapil Thangavelu",
    author_email="kapil.foss@gmail.com",
    url="http://launchpad.net/juju-deployer",
    install_requires=["jujuclient >= 0.13"],
    packages=find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers"],
    test_suite="deployer.tests",
    entry_points={
        "console_scripts": [
            'juju-deployer = deployer.cli:main']},
    )
