from setuptools import setup

setup(name='borda',
      version='0.1',
      description='Voting system based on the Borda counting scheme',
      long_description=open('README.rst', 'r').read(),
      author='Luis Osa',
      author_email='luis.osa.gdc@gmail.com',
      url='https://github.com/logc/borda',
      packages=['borda'],
      install_requires=[
          'bottle',
          'requests'],
      extras_require={
          'test': ['MiniMock']},
      entry_points={
          'console_scripts': [
          'bordad=borda.server:main',
          'borda=borda.client:run']},
      zip_safe=True,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Framework :: Bottle',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Topic :: Office/Business :: Groupware'])
