from setuptools import setup

setup(name='uttt_irc',
      version='0.1-2',
      description='An IRC bot using the uttt package',
      url='http://github.com/projectdelphai/uttt_irc',
      author='projectdelphai',
      author_email='projectdelphai@gmail.com',
      license='MIT',
      packages=['uttt_irc'],
      scripts=['bin/uttt_irc'],
      install_requires=[
        'uttt',
        ],
      zip_safe=False)
