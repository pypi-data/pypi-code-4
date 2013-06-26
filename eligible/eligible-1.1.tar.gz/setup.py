from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='eligible',
      version='1.1',
      description='Python bindings for the Eligible API',
      long_description=readme(),
      url='http://github.com/EligibleAPI/eligible-python',
      author='Sourceless',
      author_email='laurence@sourceless.org',
      license='MIT',
      packages=['eligible'],
      zip_safe=False,
      keywords='eligible api healthcare rest',
      test_suite='nose.collector',
      tests_require=['nose'])
