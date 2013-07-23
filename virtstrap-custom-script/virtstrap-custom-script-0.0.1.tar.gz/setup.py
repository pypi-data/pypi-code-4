from setuptools import setup, find_packages
import sys, os

version = '0.0.1'

setup(
    name='virtstrap-custom-script',
    version=version,
    description="A virtstrap plugin that runs a custom script on install",
    long_description="""A virtstrap plugin that installs node packages""",
    classifiers=[],
    keywords='virtstrap ruby bundler virtualenv pip',
    author='Reuven V. Gonzales',
    author_email='reuven@tobetter.us',
    url='http://github.com/ravenac95/virtstrap-custom-script',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'virtstrap-local',
    ],
    entry_points={
        'virtstrap_local.plugins': [
            'custom-script = virtstrap_custom_script.plugin',
        ]
    },
)
