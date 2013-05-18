from setuptools import setup

def readme():
    with open('README') as f:
        return f.read()

setup(name='v12',
      version='0.1.2dev',
      description='Google App Engine web framework built on webapp2',
      long_description=readme(),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          ],
      keywords='gae web framework webapp2 command line cli google app engine appengine paas build system package manager routing routes scaffolding asset pipeline fingerprint cache buster cachebuster cachebusting',
      url='http://github.com/rsimp/v12',
      author='Robert Simpson',
      author_email='robhsimpson@gmail.com',
      license='MIT',
      packages=['v12'],
      install_requires=[
          'virtualenv',
          'psutil',
          'PyYAML'
          ],
      entry_points={
          'console_scripts': ['v12=v12.cli:main'],
          },
      zip_safe=False)