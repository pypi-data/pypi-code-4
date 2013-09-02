import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = """penelope.trac
=============

for more details visit: http://getpenelope.github.com/"""
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'distribute',
    'mandrill',
    'penelope.core',
    'privatecomments',
    'python-creole',
    'sensitivetickets>=0.21',
    'Trac',
    'TracDynamicFields',
    'TracThemeEngine>=2.0',
    'TracXMLRPC',
    ]

extra = {} 
try:
    from trac.util.dist import get_l10n_cmdclass 
    cmdclass = get_l10n_cmdclass() 
    if cmdclass: # Yay, Babel is there, we've got something to do! 
        extra['cmdclass'] = cmdclass 
        extractors = [ 
            ('**.py',                'python', None), 
            ('**/templates/**.html', 'genshi', None), 
            ('**/templates/**.txt',  'genshi', { 
                'template_class': 'genshi.template:TextTemplate' 
            }), 
        ] 
        extra['message_extractors'] = { 
            'penelope/trac': extractors, 
        }
except ImportError: 
    pass 


setup(name='penelope.trac',
      version='1.1',
      description='Penelope: Trac integration',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        ],
      author='Penelope Team',
      author_email='penelopedev@redturtle.it',
      url='http://getpenelope.github.com',
      keywords='web wsgi bfg pylons pyramid',
      namespace_packages=['penelope'],
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='penelope.trac',
      install_requires = requires,
      entry_points = {
          'console_scripts': [
            'auth_wsgi = penelope.trac.auth_wsgi:main',
          ],
          'trac.plugins': [
            'penelope.trac = penelope.trac.plugins',
            'penelope.trac.users = penelope.trac.user',
            'penelope.trac.communication = penelope.trac.communication',
            'penelope.trac.workflow = penelope.trac.workflow',
          ]
      },
      **extra
      )
