from setuptools import setup

setup(name='eligible',
      version='1.1.2',
      description='Python bindings for the Eligible API',
      url='http://github.com/EligibleAPI/eligible-python',
      author='Sourceless',
      author_email='laurence@sourceless.org',
      license='MIT',
      packages=['eligible'],
      zip_safe=False,
      keywords='eligible api healthcare rest',
      test_suite='nose.collector',
      tests_require=['nose'])
