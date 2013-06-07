from distutils.core import setup

setup(
    name='herokufu',
    version='0.0.3',
    author="John Mark Schofield",
    author_email="jms@schof.org",
    packages=['herokufu', ],
    scripts=['hfu', ],
    url="http://pypi.python.org/pypi/herokufu",
    license='LICENSE.txt',
    description="Utilities to run Django & Mezzanine on Heroku",
    long_description=open('README.txt').read(),
)
