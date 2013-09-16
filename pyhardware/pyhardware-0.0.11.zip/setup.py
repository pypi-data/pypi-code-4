import os
from setuptools import setup
from setuptools.command.install import install
import subprocess
import shutil


class installWithPost(install):
    def run(self):
        install.run(self)
        build_folder = os.path.join(os.environ['TEMP'], 
                                    'pip_build_' + os.environ['USERNAME'],
                                    'pyivi')
        if os.path.exists(build_folder):
            shutil.rmtree(build_folder)
        if subprocess.call(['pip', 
                         'install',
                         'pyivi', 
                         '-I', 
                         '-U']):
            raise RuntimeError('problem installing pyivi')

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pyhardware",
    cmdclass={"install": installWithPost},
    scripts={'postinstallscript.py'},
    version = "0.0.11",
    author = "Samuel Deleglise",
    author_email = "samuel.deleglise@gmail.com",
    description = ("""Control of data acquisition with remote instruments using 
    IVI-COM, or IVI-C, Visa, and serial protocols."""),
    license = "BSD",
    keywords = "instruments data-acquisition IVI interface",
    url = "https://github.com/SamuelDeleglise/pyinstruments",
    packages=['pyhardware',
              'pyhardware/config',
              'pyhardware/config/gui',
              'pyhardware/drivers',
              'pyhardware/drivers/ivi',
              'pyhardware/drivers/serial',
              'pyhardware/drivers/visa',
              'pyhardware/utils',
              'pyhardware/utils/conf_xml',
              'pyhardware/utils/curve',
              'pyhardware/utils/guiwrappersutils'],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Scientific/Engineering :: Human Machine Interfaces",
        "License :: OSI Approved :: BSD License",
    ],
    install_requires=[]
)