from setuptools import setup, find_packages
from version import get_git_version


setup(name='fose',
        version=get_git_version(),
        description='Framework for Open Science Evaluation Core Package',
        author='Jasper van den Bosch',
        author_email='jasper.jf.vandenbosch@gmail.com',
        url='https://github.com/ilogue/fose',
        packages=find_packages(),
        test_suite='tests',
        entry_points={
          'console_scripts': ['fose = fose:main',]},
        install_requires=['lxml','requests'],
        package_data={'fose': ['*.xsd']},
      )

