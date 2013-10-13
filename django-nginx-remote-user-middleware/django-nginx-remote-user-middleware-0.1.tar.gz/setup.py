from setuptools import setup

setup(
    name="django-nginx-remote-user-middleware",
    version="0.1",
    description='A drop-in middleware for Django which passes through REMOTE_USER variables set by reverse proxies',
    author='Chris Northwood',
    author_email='chris@pling.org.uk',
    license='BSD',
    py_modules=['djangonginxremoteusermiddleware'],
    install_requires=['Django']
)