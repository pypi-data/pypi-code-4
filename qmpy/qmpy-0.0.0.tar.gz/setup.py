from distutils.core import setup

setup(
    name='qmpy',
    version='0.0.0',
    author='S. Kirklin',
    author_email='scott.kirklin@gmail.com',
    packages=['qmpy'],
    scripts=[],
    url='http://pypi.python.org/pypi/qmpy',
    license='LICENSE.txt',
    description='Suite of computational materials science tools',
    long_description=open('README.txt').read(),
    install_requires=[
        "Django >= 1.1.1",
        "Pulp >= 1.4.0",
        "numpy >= 1.6.4"
    ],
)
