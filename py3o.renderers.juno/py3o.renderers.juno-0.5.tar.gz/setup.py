from setuptools import setup, find_packages

version = '0.5'

setup(name='py3o.renderers.juno',
      version=version,
      description="A Java based driver for py3o",
      long_description=open("README.txt").read(),
      classifiers=[
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: BSD License",
          "Operating System :: OS Independent",
          "Programming Language :: Java",
          "Programming Language :: Python :: 2",
          "Topic :: Printing",
      ],
      keywords='LibreOffice OpenOffice PDF',
      author='Florent Aide & Jerome Collette',
      author_email='florent.aide@gmail.com, collette.jerome@gmail.com',
      url='http://bitbucket.org/faide/py3o.renderers.juno',
      dependency_links=[],
      license='BSD License',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['py3o'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          'jpype',
      ],
      entry_points=dict(
      # -*- Entry points: -*-
      ),
      test_suite='nose.collector',
      )
