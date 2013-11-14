from setuptools import setup, find_packages


tests_require = []

install_requires = [
    'watchdog',
    'fabric',
]

setup(name='fabuild',
      version='0.0.3',
      description='Script-based build system build on top of Fabric',
      author='John Nadratowski',
      author_email='jnadro52@gmail.com',
      url='https://github.com/johnnadratowski/fabuild',
      packages=find_packages(),
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require={'test': tests_require},
      include_package_data=True,
      zip_safe=False,
      classifiers=[
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'Operating System :: OS Independent',
          'Topic :: Software Development'
      ],
)
