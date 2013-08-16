from distutils.core import setup

setup(
    name='jsonquery',
    version='0.2.1',
    author='Joe Cross',
    author_email='joe.mcross@gmail.com',
    packages=['jsonquery'],
    url='https://github.com/numberoverzero/jsonquery',
    license='LICENSE.txt',
    description='Lightweight bit packing for classes',
    long_description=open('README.rst').read(),
    install_requires=["SQLAlchemy >= 0.8.2"],
    requires=["SQLAlchemy"],
)
