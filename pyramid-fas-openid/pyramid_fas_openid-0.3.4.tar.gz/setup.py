import os
from setuptools import setup, find_packages
version = '0.3.4'
README = os.path.join(os.path.dirname(__file__), 'README.txt')
long_description = open(README).read()

setup(name='pyramid_fas_openid',
        version=version,
        url='http://github.com/lmacken/pyramid_fas_openid',
        description=('A view for pyramid that functions as an '
            'OpenID consumer.'),
        long_description=long_description,
        classifiers=['Framework :: Pylons',
            'Intended Audience :: Developers',
            'License :: Repoze Public License',
            'Programming Language :: Python',
            'Topic :: Internet :: WWW/HTTP',
            'Topic :: Internet :: WWW/HTTP :: WSGI'],
        keywords='pyramid openid',
        author='Luke Macken, Thomas Hill',
        author_email='lmacken@redhat.com',
        license='BSD-derived (http://www.repoze.org/LICENSE.txt)',
        packages=find_packages(),
        install_requires=['pyramid', 'python-openid', 'python-openid-teams',
                          'python-fedora']
)
