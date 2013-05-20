from setuptools import setup, find_packages

setup(name='irccat3',
      version='0.1',
      description='IRCCat in Python',
      author='Joshua D. Boyd',
      author_email='jdboyd@jdboyd.net',
      url='https://github.com/jd-boyd/irccat3',
      packages=find_packages(),
      install_requires=['argparse', 'irc'],
      tests_require=['nose'],
      entry_points={'console_scripts': ['irccat3 = irccat3.main:main',]}
     )
