from distutils.core import setup

setup(
    name='suds_cascade',
    version='0.1.0',
    author='Camilo Payan',
    author_email='cpayan@fiu.edu',
    packages=['suds_cascade'],
    url='http://pypi.python.org/pypi/suds_cascade/',
    license='LICENSE.txt',
    description='Cascade CMS Web Services Client based on Suds',
    long_description=open('README.txt').read(),
    install_requires=[
        "suds == 0.4",
    ],
)
