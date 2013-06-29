from setuptools import setup

setup(name='uttt',
      version='0.3-1',
      description='An Ultimate Tic Tac Toe Class',
      url='http://github.com/projectdelphai/uttt_irc',
      author='projectdelphai',
      author_email='projectdelphai@gmail.com',
      license='MIT',
      packages=['uttt'],
      data_files=[('/etc/uttt', ['uttt/data/game_data'])],
      zip_safe=False)
