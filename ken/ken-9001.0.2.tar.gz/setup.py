from setuptools import setup


with open('README.md', 'r') as f:
    long_description = f.read()


setup(name="ken",
      version="9001.0.2",
      description="Ken is over 9000",
      long_description=long_description,
      py_modules=["ken"],
      author="Infoshift Inc",
      author_email="me@jpanganiban.com")
