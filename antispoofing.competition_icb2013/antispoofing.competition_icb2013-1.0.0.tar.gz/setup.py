#!/usr/bin/env python
# Ivana Chingovska <ivana.chingovska@idiap.ch>
#Mon Feb 11 18:29:44 CET 2013

from setuptools import setup, find_packages

# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    name='antispoofing.competition_icb2013',
    version='1.0.0',
    description='Fusion of spoofing counter measures for the REPLAY-ATTACK database (competition entry for 2nd competition on counter measures to 2D facial spoofing attacks, ICB 2013)',
    url='http://pypi.python.org/pypi/antispoofing.competition_icb2013',
    license='GPLv3',
    author='Ivana Chingovska',
    author_email='ivana.chingovska@idiap.ch',
    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,

    namespace_packages=[
      "antispoofing",
      ],

    install_requires=[
      "setuptools",
      "bob >= 1.1.0",
      "xbob.db.replay", # Replay-Attack database
      "xbob.db.casia_fasd", #CASIA database
      "antispoofing.utils",  #Utils Package
      "antispoofing.fusion",  #Fusion Package
      "antispoofing.lbptop",  #LBPTOP Package
      "antispoofing.lbp", # LBP package
      "antispoofing.motion", # Motion package
    ],

    entry_points={
      'console_scripts': [
        'calcglcm.py = antispoofing.competition_icb2013.script.calcglcm:main',
        'crop_faces.py = antispoofing.competition_icb2013.script.crop_faces:main',
        'ldatrain.py = antispoofing.competition_icb2013.script.ldatrain:main',
        'svmtrain.py = antispoofing.competition_icb2013.script.svmtrain:main',
        'icb2013_qstatistic.py = antispoofing.competition_icb2013.script.icb2013_qstatistic:main',
        'icb2013_facebb_countermeasure.py = antispoofing.competition_icb2013.script.icb2013_facebb_countermeasure:main',
        'apply_threshold.py = bob.measure.script.apply_threshold:main',
        'eval_threshold.py = bob.measure.script.eval_threshold:main',
        ],
      },

)
