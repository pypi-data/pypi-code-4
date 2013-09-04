from setuptools import setup, find_packages
readme = open('README.md').read()
setup(name='SimpleRender',
      version='0.1.2',
      author='Nick Otter',
      author_email='otternq@gmail.com',
      url='https://github.com/otternq/SimpleRender',
      license='MIT',
      description='Takes a config file and a template and renders',
      long_description=readme,
      packages=find_packages(),
      scripts=['bin/render.py'])