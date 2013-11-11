from setuptools import setup, find_packages
from os.path import join

name = 'dolmen.app.authentication'
version = '1.1.1'
readme = open(
    join('src', 'dolmen', 'app', 'authentication', 'README.txt')).read()
history = open(
    join('docs', 'HISTORY.txt')).read().replace(name + ' - ', '')


install_requires=[
    'dolmen.authentication >= 0.2',
    'dolmen.forms.base',
    'dolmen.forms.crud',
    'grok',
    'grokcore.component',
    'grokcore.content',
    'grokcore.layout',
    'grokcore.view',
    'setuptools',
    'z3c.schema',
    'zeam.form.base',
    'zope.authentication',
    'zope.component',
    'zope.container',
    'zope.event',
    'zope.formlib',
    'zope.i18n',
    'zope.i18nmessageid',
    'zope.interface',
    'zope.location',
    'zope.pluggableauth >= 1.1',
    'zope.principalregistry',
    'zope.publisher',
    'zope.schema',
    'zope.security',
    'zope.securitypolicy',
    'zope.site',
    'zope.traversing',
    ]

test_requires = [
    'dolmen.app.site',
    'zope.app.appsetup',
    'zope.app.publication',
    'zope.app.wsgi >= 3.9.2',
    'zope.browserpage',
    'zope.i18n',
    'zope.testing',
    'zope.dublincore',
    ]

setup(name = name,
      version = version,
      description = 'Dolmen CMS authentication package',
      long_description = readme[readme.find('\n\n'):] + '\n' + history,
      keywords = 'Grok Zope3 CMS Dolmen',
      author = 'Souheil Chelfouh',
      author_email = 'souheil@chelfouh.com',
      url = 'http://tracker.trollfot.org/',
      download_url = 'http://pypi.python.org/pypi/dolmen.app.authentication',
      license = 'GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages = ['dolmen', 'dolmen.app'],
      include_package_data = True,
      platforms = 'Any',
      zip_safe = False,
      extras_require={'test': test_requires},
      install_requires=install_requires,
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Zope3',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
      ],
)
