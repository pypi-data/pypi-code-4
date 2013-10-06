from setuptools import setup

setup(
    name="flask-args",
    version="0.3.0",
    description="auto type convertion for flask.request.form/args/values",
    long_description=open('test_flask_args.py').read(),
    license="MIT",
    packages=['flask_args'],
    install_requires=['Flask'],
)
