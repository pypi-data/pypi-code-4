from setuptools import setup, find_packages

setup(name='ResourceValidator',
      author='Nick Dumas',
      author_email="drakonik@gmail.com",
      version='.1',
      packages=find_packages(),
      entry_points = {
          'console_scripts': ['resource_check = resource_validator.app:main']
      }
      )
