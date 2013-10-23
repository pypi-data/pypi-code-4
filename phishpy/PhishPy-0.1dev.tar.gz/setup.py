from distutils.core import setup

setup(
    name='PhishPy',
    url='https://github.com/zwass/PhishPy',
    author='Zachary Wasserman',
    author_email='zachwass2000@gmail.com',
    version='0.1dev',
    packages=['phishpy'],
    license=open('LICENSE').read(),
    description='Wrapper for the Phish.net API',
    long_description=open('README').read(),
)
