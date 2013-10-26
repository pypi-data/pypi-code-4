from setuptools import setup, find_packages

setup(
    entry_points={
        "console_scripts": [
            "OQToolsUI = oqtoolsui.oqtools.main:main",
            ],
        },
    install_requires=['openquake.hazardlib<=0.11.0', 'openquake.nrmllib<=0.4.5', 'pyshp'],
    name='OQToolsUI',
    version='1.0.3',
    packages=['oqtoolsui', 'oqtoolsui.common', 'oqtoolsui.controllers', 'oqtoolsui.converters', 'oqtoolsui.oqtools',
              'oqtoolsui.ui'],
    package_data={'oqtoolsui.oqtools': ['intensityLevels.txt', 'job.ini.template']},
    classifiers=(
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Education',
        'Topic :: Scientific/Engineering'
    ),
    url='http://github.com/ocozalp/OQToolsUI',
    license='GNU Affero General Public License v3',
    author='Orhan Can Ozalp',
    author_email='ozalp.orhan@gmail.com',
    description='UI for openquake'
)
