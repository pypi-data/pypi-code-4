from distutils.core import setup

setup(
    name='ssl_sni',
    version='0.1',
    author='Alex Orange',
    author_email='crazycasta@gmail.com',
    packages=['ssl_sni'],
    url='https://pypi.python.org/pypi/ssl_sni/0.1',
    license='LICENSE',
    description='A wrapper to pyOpenSSL to provide an interface like the standard ssl module.',
    long_description=open('README').read(),
    install_requires=['pyOpenSSL >= 0.13',
                      'pyasn1 >= 0.1.7']
)
