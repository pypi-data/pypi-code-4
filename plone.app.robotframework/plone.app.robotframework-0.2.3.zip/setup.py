from setuptools import setup
from setuptools import find_packages

version = '0.2.3'

long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n'
)

console_scripts = [
    "robot-server = plone.app.robotframework.server:server",
    "robot = plone.app.robotframework.robotentrypoints:robot",
    "ride = plone.app.robotframework.robotentrypoints:ride",
]

entry_points = dict(console_scripts=console_scripts)

install_requires = [
    'setuptools',
    # Utility dependencies:
    'argparse',
    # Plone testing dependencies:
    'plone.testing',
    'plone.app.testing',  # [robot] >= 4.2.2 would include Robot deps.
    # Functional Robot testing dependencies:
    'robotsuite',
    'robotframework',
    'robotframework-selenium2library',
    # Implicit Robot Framework dependencies:
    'decorator',
    'selenium',
]

ride_requires = [
    # GUI
    'robotframework-ride'
]

reload_requires = [
    # Watch for filesystem changes:
    'watchdog'
]

setup(
    name='plone.app.robotframework',
    version=version,
    description="Robot Framework testing resources for Plone",
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python",
    ],
    keywords='',
    author='Asko Soukka',
    author_email='asko.soukka@iki.fi',
    url='https://github.com/plone/plone.app.robotframework/',
    license='gpl',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['plone', 'plone.app'],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require={'ride': ride_requires,
                    'reload': reload_requires},
    entry_points=entry_points,
)
