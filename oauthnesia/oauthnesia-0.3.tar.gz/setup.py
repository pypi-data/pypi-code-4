from setuptools import setup

setup(name='oauthnesia',
      version='0.3',
      description='Client for Urbanesia\'s OAUTH v1.0a API',
      url='http://github.com/Urbanesia/oauthnesia',
      author='Batista Harahap',
      author_email='tista@urbanesia.com',
      license='MIT',
      packages=['oauthnesia'],
      install_requires=[
          'requests',
          'requests_oauthlib',
          'json'],
      zip_safe=False)