from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    )

tests_require = [
    'zope.app.wsgi [test]',
    'zope.configuration',
    'zope.testing',
    ]

setup(
    name='grokcore.formlib',
    version='1.10a1',
    author='Grok Team',
    author_email='grok-dev@zope.org',
    url='http://grok.zope.org',
    download_url='http://cheeseshop.python.org/pypi/grokcore.formlib',
    description='Grok-like configuration for zope.formlib components',
    long_description=long_description,
    license='ZPL',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Framework :: Zope3',
        ],
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages=['grokcore'],
    include_package_data = True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'grokcore.component >= 2.1',
        'grokcore.security >= 1.5',
        'grokcore.view >= 2.0',
        'martian >= 0.13',
        'pytz',
        'zope.container',
        'zope.event',
        'zope.formlib >= 4.3.0a2.dev0',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.publisher',
        'zope.schema',
        ],
    tests_require=tests_require,
    extras_require={'test': tests_require},
)
