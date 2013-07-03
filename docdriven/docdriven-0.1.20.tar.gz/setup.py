from distutils.core import setup

setup(
    name='docdriven',
    version='0.1.20',
    author='Jon Crowell',
    author_email='docdriven@JonCrowell.org',
    packages=['docdriven'],
    #scripts=['docdriver.py'],
    url='http://pypi.python.org/pypi/docdriven/',
    license='MIT_LICENSE.txt',
    description='Support for documentation-driven development of JSON APIs.',
    long_description=open('docs/docdriven.dd').read(),
    requires=["requests (>=1.2.0)"],
    provides=[ "docdriven" ],
    )

