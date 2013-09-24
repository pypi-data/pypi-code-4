from setuptools import setup, find_packages

version = '0.2'

setup(name='wheelcms_comments',
      version=version,
      description="WheelCMS comments package",
      long_description=open("README.md").read(),
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Ivo van der Wijk',
      author_email='wheelcms@in.m3r.nl',
      url='http://github.com/wheelcms/wheelcms_comments',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=[],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'pytest',
          'django-simple-captcha'
      ],
      entry_points={
      },

      )

