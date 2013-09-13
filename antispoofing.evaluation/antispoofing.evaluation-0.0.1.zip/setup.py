#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Ivana Chingovska <ivana.chingovska@idiap.ch>
# Fri Sep  6 12:26:13 CEST 2013

from setuptools import setup, find_packages

# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    name='antispoofing.evaluation',
    version='0.0.1',
    description='Evaluation tools for verification systems under spoofing attacks: examples in face verification',
    url='http://github.com/bioidiap/antispoofing.evaluation',
    license='LICENSE.txt',
    author_email='Ivana Chingovska <ivana.chingovska@idiap.ch>',
    #long_description=open('doc/howto.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),

    install_requires=[
        "bob",      # base signal proc./machine learning library
        "argparse", # better option parsing
    ],

    entry_points={
      'console_scripts': [
        'score_distr_generator.py = antispoofing.evaluation.script.score_distr_generator:main',
        'plot_on_demand.py = antispoofing.evaluation.script.plot_on_demand:main',
        'plot_faceverif_comparison.py = antispoofing.evaluation.script.plot_faceverif_comparison:main',
        'plot_fusionmethods_comparison.py = antispoofing.evaluation.script.plot_fusionmethods_comparison:main',
        'plot_countermeasures_comparison.py = antispoofing.evaluation.script.plot_countermeasures_comparison:main',
        'calc_aue_value.py = antispoofing.evaluation.script.calc_aue_value:main',
        'apply_threshold.py = bob.measure.script.apply_threshold:main',
        'eval_threshold.py = bob.measure.script.eval_threshold:main',
        ],
      },

)
