'''Author: Sourabh Bajaj'''
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

setup(
    author='Sourabh Bajaj',
    author_email='sourabhbajaj90@gmail.com',
    
    packages=find_packages(),
    namespace_packages=['QuickCommand'],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
      ],
    description='Python package to create commands for everyday use.',
    long_description=open('README.md').read(),

    entry_points={
        'console_scripts': [
            'cppcompile=QuickCommand.commands:cppcompile'
            ],
        },

    include_package_data=True,
    license=open('LICENSE.txt').read(),

    name='QuickCommand',
    version='0.1.0',
    url='https://github.com/sb2nov/QuickCommand',
    zip_safe=True,
)
