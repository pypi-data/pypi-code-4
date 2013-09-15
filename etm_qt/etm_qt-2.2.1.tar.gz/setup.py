#  from setuptools import setup, find_packages
# from distutils.core import setup
from setuptools import setup
from etmQt.v import version
import etmQt

setup(
    name='etm_qt',
    version=version,
    url='http://people.duke.edu/~dgraham/etmqt',
    description='event and task manager',
    long_description='manage events and tasks using simple text files',
    platforms='Any',
    license='License :: OSI Approved :: GNU General Public License (GPL)',
    author='Daniel A Graham',
    author_email='daniel.graham@duke.edu',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows :: Windows XP',
        'Operating System :: Microsoft :: Windows :: Windows Vista',
        'Operating System :: Microsoft :: Windows :: Windows 7',
        'Operating System :: OS Independent',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Topic :: Office/Business',
        'Topic :: Office/Business :: News/Diary',
        'Topic :: Office/Business :: Scheduling',
        ],
    packages=['etmQt',],
    scripts=['etm_qt.py'],
    install_requires=["python-dateutil>=1.5", "PyYaml>=3.10"],
    package_data={'etmQt': ['help/*/*', 'language/*/*', 'version.txt', 'CHANGES', 'INSTALL.html', 'etm_qt.1', 'icons/etmlogo_48x48x32.ico']},
)
