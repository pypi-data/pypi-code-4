from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='oauthnesia',
      version='1.0',
      description='Client for Urbanesia\'s OAUTH v1.0a API',
      long_description=readme(),
      keywords='urbanesia oauth poi web service api',
      url='http://github.com/Urbanesia/oauthnesia-py',
      author='Batista Harahap',
      author_email='tista@urbanesia.com',
      license='MIT',
      packages=['oauthnesia'],
      install_requires=[
          'requests',
          'requests_oauthlib',
          'json'],
      zip_safe=False)