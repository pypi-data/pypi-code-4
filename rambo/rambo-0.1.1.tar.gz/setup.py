from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='rambo',
      version='0.1.1',
      description='Ram your images into CSS sprites with Rambo',
      long_description=readme(),
      url='https://github.com/springload/rambo',
      author='Springload',
      author_email='josh@springload.co.nz',
      license='MIT',
      packages=['rambo'],
      install_requires=['pil', 'argparse'],
      scripts=['bin/rambo'],
      zip_safe=False)