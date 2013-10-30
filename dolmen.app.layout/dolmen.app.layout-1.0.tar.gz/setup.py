from setuptools import setup, find_packages
from os.path import join

name = 'dolmen.app.layout'
version = '1.0'
readme = open(join('src', 'dolmen', 'app', 'layout', 'README.txt')).read()
history = open(join('docs', 'HISTORY.txt')).read()

install_requires = [
    'dolmen.app.security',
    'dolmen.forms.crud >= 1.0b1',
    'dolmen.menu',
    'grokcore.message',
    'grokcore.security',
    'grokcore.view',
    'grokcore.viewlet',
    'grokcore.layout',
    'megrok.resourceviewlet >= 0.2',
    'setuptools',
    'zope.container',
    'zope.interface',
    'zope.location',
    'zope.publisher',
    'zope.traversing',
    ]

tests_require = [
    'dolmen.content',
    'grokcore.component',
    'zope.component',
    'zope.container',
    'zope.i18n',
    'zope.principalregistry',
    'zope.publisher',
    'zope.security',
    'zope.securitypolicy',
    'zope.site',
    'zope.traversing',
    ]

setup(name = name,
      version = version,
      description = 'Layout and page models for Dolmen applications',
      long_description = readme + '\n\n' + history,
      keywords = 'Grok Zope3 CMS Dolmen',
      author = 'Souheil Chelfouh',
      author_email = 'trollfot@gmail.com',
      url = 'http://gitweb.dolmen-project.org/',
      download_url = '',
      license = 'GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages = ['dolmen', 'dolmen.app'],
      include_package_data = True,
      platforms = 'Any',
      zip_safe = False,
      tests_require = tests_require,
      install_requires = install_requires,
      extras_require = {'test': tests_require},
      test_suite="dolmen.app.layout",
      classifiers = [
        'Environment :: Web Environment',
        'Framework :: Zope3',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
      ])
