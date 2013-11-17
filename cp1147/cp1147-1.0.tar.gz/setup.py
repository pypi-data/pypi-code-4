from setuptools import setup, find_packages

setup(name="cp1147",
      version="1.0",
      author='Denis Wallerich',
      author_email='denis.wallerich@datim.fr',
      url = "http://www.datim.fr",
      packages=find_packages(),
      include_package_data=True,
      license='BSD',
      description = 'cp1147 EBCDIC french (euro) codec',
      long_description=open('README.rst').read(),
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: System :: Hardware :: Mainframes",
        "License :: OSI Approved :: BSD License",
       ],
     )

