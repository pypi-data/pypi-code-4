from setuptools import setup, find_packages

version = '0.1'


def read_description():
    with open('README.rst') as f:
        return f.read()

setup(name='shooju',
      version=version,
      description="Official Shooju Client",
      long_description=read_description(),
      keywords='data, client, shooju',
      author='Aldo Garcia',
      author_email='aldo@shooju.com',
      url='http://shooju.com',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "requests>=2.0.0"
      ]
      )
