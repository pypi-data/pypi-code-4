from distutils.core import setup
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='jinja2-pluralize-filter',
    version='0.0.2',
    author='Yuri Shikanov',
    author_email='dizballanze@gmail.com',
    packages=['pluralize'],
    # scripts=[],
    url='https://github.com/dizballanze/jinja2-pluralize-filter',
    license='MIT',
    description='Simple jinja2 filter to choose correct plural form for Russian language.',
    long_description=read('README.rst'),
    install_requires=[
        "pytils == 0.2.3",
        "Jinja2 == 2.7",
    ],
    data_files=[('', ['LICENSE', 'README.rst'])]
)