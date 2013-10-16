from setuptools import setup, find_packages

setup(name='ResourceValidator',
      author='Nick Dumas',
      author_email="drakonik@gmail.com",
      version='alpha',
      packages=find_packages(),
      entry_points = {
          'console_scripts': ['image_check = image_checker.img_check:main']
      }
      )
