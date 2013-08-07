from setuptools import setup, find_packages

setup(
    name='jira-bulk-loader',
    version='0.1.8',
    packages=['jirabulkloader','jirabulkloader.test',],
    author='Alexander Dudko',
    author_email='alex.dudko@gmail.com',
    license='GPLv3',
    url='http://bitbucket.org/oktopuz/jira-bulk-loader',
    scripts=['bin/jira-bulk-loader.py'],
    description='An automation tool for creating tasks in Jira via RESTful API',
    long_description=open('README.rst').read(),
    install_requires=[
        "simplejson >= 3.3.0",
        "requests >= 0.13.1",
        "argparse >= 1.2.1",
        "pytest >= 2.3.5",
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Information Technology',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],
)
