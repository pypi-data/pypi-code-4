from setuptools import setup

setup(name='randomdata',
      version='0.1a.dev3',
      description='Random data generator.  Creates CSV data files with generated(random) data.',
      author='Rodolfo Duldulao, Jr.',
      author_email='rnduldulaojr@gmail.com, rduldulao@chikka.com',
      url='https://bitbucket.org/dulds/randomdata/overview',
      license='BSD',
      packages=['randomdata'],
      install_requires=['rstr'],
      classifiers=[
            "Development Status :: 2 - Pre-Alpha",
            "Environment :: Console",
            "Topic :: Utilities"
      ]
)
