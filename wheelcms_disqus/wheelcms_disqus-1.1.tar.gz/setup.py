from setuptools import setup, find_packages
import os

version = '1.1'

setup(name='wheelcms_disqus',
      version=version,
      description="WheelCMS Disqus comment support",
      long_description=open("README.md").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Ivo van der Wijk',
      author_email='wheelcms@in.m3r.nl',
      url='http://github.com/wheelcms/wheelcms_disqus',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=[],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'wheelcms_axle',
          'setuptools',
          'pytest',
      ],
      entry_points={
      },

      )

