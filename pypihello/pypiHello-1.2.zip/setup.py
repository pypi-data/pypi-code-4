from setuptools import setup, find_packages
#
setup(name='pypiHello',#
      version='1.2',#
      description='A simple example',#
      author='bluemsn',#
      # py_modules=['hello',#
      #             'hello_project/example',
      #             'hello_project/test']

      packages=find_packages(),
)


#
# from setuptools import setup, find_packages
# import sys, os
#
# version = '0.1'
#
# setup(name='pypiHello',
#       version=version,
#       description="a link tester written in python",
#       long_description="""\
# """,
#       classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
#       keywords='python',
#       author='blue    msn',
#       author_email='bluemsn@126.com',
#       license='',
#       packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
#       include_package_data=True,
#       zip_safe=False,
#       install_requires=[
#           # -*- Extra requirements: -*-
#       ],
#       entry_points={
#       },
#       )

