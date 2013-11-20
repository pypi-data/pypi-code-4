import platform

from distutils.core import setup

setup_params = dict(
    name='cspkeyset',
    version='0.1.9',
    url='https://bitbucket.org/andviro/cspkeyset',
    packages=['cspkeyset'],
    scripts=['keyset'],
    install_requires=['pyasn1', 'cryptoapy>=0.4.32', 'rarfile'],
    license='LGPL',
    author='Andrew Rodionoff',
    author_email='andviro@gmail.com',
    description='CSP keyset management (currently Linux CryptoPro CSP hdimages only)',
)

setup(**setup_params)
