from setuptools import setup

setup(
    name="xmpp_logging_handler",
    author='Raymond McGinlay',
    author_email='Raymond McGinlay',
    url='http://www.thisislevelup.com/',
    version='1.0.2',
    packages=['xmpp_logging_handler', ],
    install_requires=[
        'xmpppy', ],
    license='GPL v3 or higher',
    description='A python logging framework handler sending to an xmpp server',
    long_description = open('README.txt').read(),
)
