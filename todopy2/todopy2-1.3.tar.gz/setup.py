import os
from setuptools import setup, find_packages

root_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(root_dir, "README.md")) as f:
    README = f.read()

setup(
    name='todopy2',
    version='1.3',
    description='Simple to-do list CLI manager in Python',
    long_description=README,
    url='https://github.com/kotnik/todopy2',
    license='GPLv3+',
    author='Nikola Kotur',
    author_email='kotnick@gmail.com',
    packages=find_packages(exclude=['tests*']),
    scripts=[
        "bin/todo",
    ],
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Office/Business :: Scheduling',
    ],
)
