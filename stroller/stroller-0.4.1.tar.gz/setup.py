from setuptools import setup, find_packages
import sys, os

version = '0.4.1'

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
except IOError:
    README = ''

setup(name='stroller',
      version=version,
      description="E-commerce Application and Library for TurboGears2",
      long_description=README,
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Framework :: TurboGears",
          "Topic :: Office/Business :: Financial :: Point-Of-Sale",
          "Topic :: Internet :: WWW/HTTP :: Dynamic Content"
      ],
      keywords='turbogears2.application turbogears2.extension ecommerce paypal shop',
      author='AXANT',
      author_email='tech@axant.it',
      url='https://bitbucket.org/_amol_/stroller',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      package_data = {'':['*.html', '*.js', '*.css', '*.png', '*.jpg', '*.gif']},
      message_extractors = {'stroller': [
         ('**.py', 'python', None),
         ('templates/**.mako', 'mako', None),
         ('templates/**.html', 'genshi', None),
         ('public/**', 'ignore', None)]},
      zip_safe=False,
      install_requires=[
      "PIL>=1.1.7",
      "Babel",
      "tw.dynforms",
      "tw.jquery",
      "TurboGears2 >= 2.1.4",
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
     )
