from setuptools import setup, find_packages
import svnversion

requires = ['WebError','mock', 'webtest', 'BeautifulSoup4','shortuuid','requests','zope.interface','zope.component']

setup(name='readable',
      version=svnversion.add_revision('0.0'),
      description='testing and assertion library',
      long_description='',
      classifiers=[
        "Programming Language :: Python",
        "License :: Other/Proprietary License",
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        ],
      author='Jasper van den Bosch',
      author_email='jasper@ilogue.com',
      url='http://ilogue.com',
      keywords='',
      packages=find_packages(),
      namespace_packages = ['ilogue'],
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      test_suite="ilogue.readable.tests.fast",
      )

## to run the slow test suite, execute
# env/bin/python setup.py test -q --test-suite ilogue.readable.tests.slow

