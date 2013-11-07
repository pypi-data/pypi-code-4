from setuptools import setup
import requests_debug_version


setup(
    name="requests_debug",
    description="Adds logging and timing for the requests library",
    version=requests_debug_version.__version__,
    url="https://github.com/ericmoritz/requests_debug",
    author="Eric Moritz",
    author_email="eric@themoritzfamily.com",
    py_modules=["requests_debug", "requests_debug_version"],
    install_requires=[
        "simpleflake>=0.1.2,<0.2",
        "requests>=0.13,<0.14",
        ]
    )
