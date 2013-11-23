from setuptools import setup, find_packages

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='funniest_joke',
      version='0.1',
      description='The funniest joke in the world.',
      long_description=readme(),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          'Topic :: Text Processing :: Linguistic',
      ],
      keywords='funniest joke comedy flying circus',
      url='http://github.com/webee/funniest',
      author='webee',
      author_email='webee.yw@gmail.com',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'tests','tests.*']),
      # copy scripts to python/bin.
      scripts=['bin/funniest-joke'],
      # copy to site-packages.
      include_package_data=True,
      # command line entry points.
      entry_points={
          'console_scripts': ['funniest-joke-cli=funniest.command_line:main'],
      },
      # pypi deps.
      install_requires=[
          'markdown',
      ],
      # other deps.
      dependency_links=[
      ],
      zip_safe=False,
      # tests
      test_suite='nose.collector',
      tests_require=['nose'],
)
