from setuptools import setup


setup(
    name='django_dirty_bits',
    version='0.1.3.2',
    description="Dirty bits checking for Django models",
    author='Michael Milkin',
    author_email='mmilkin@gmail.com',
    py_modules=['dirty_bits'],
    install_requires=['django'],
)
