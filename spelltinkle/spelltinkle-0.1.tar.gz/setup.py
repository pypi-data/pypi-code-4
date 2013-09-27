from distutils.core import setup


setup(name='spelltinkle',
      version='0.1',
      description='Terminal text editor',
      long_description=open('README.txt').read(),
      author='J. J. Mortensen',
      author_email='jj@smoerhul.dk',
      url='https://launchpad.net/husk',
      packages=['spelltinkle', 'spelltinkle/test'],
      scripts=['scripts/spelltinkle', 'scripts/spt'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: ' +
          'GNU General Public License v3 or later (GPLv3+)',
          'Operating System :: Unix',
          'Programming Language :: Python :: 3.3',
          'Topic :: Text Editors :: Text Processing'])
