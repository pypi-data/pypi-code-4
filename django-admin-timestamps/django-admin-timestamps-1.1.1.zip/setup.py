import codecs
from os.path import join, dirname
from setuptools import setup

version = '1.1.1'
read = lambda *rnames: unicode(codecs.open(join(dirname(__file__), *rnames),
                                           encoding='utf-8').read()
                              ).strip()


setup(
    name='django-admin-timestamps',
    version=version,
    description='Custom list display of model timestamps for Django Admin.',
    long_description='\n\n'.join((read('README'), read('CHANGES'),)),
    author='Jaap Roes',
    author_email='jaap.roes@gmail.com',
    url='https://bitbucket.org/jaap3/django-admin-timestamps/',
    package_dir={'': 'src'},
    packages=['admintimestamps', 'admintimestamps.compat'],
    license='MIT',
    classifiers=[
      'Development Status :: 5 - Production/Stable',
      'Environment :: Web Environment',
      'Framework :: Django',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: MIT License',
      'Operating System :: OS Independent',
      'Programming Language :: Python',
    ],
    tests_require=['Django>=1.2', 'unittest2>=0.5.1'],
    test_suite='tests.runtests.runtests',
    zip_safe=False,
)
