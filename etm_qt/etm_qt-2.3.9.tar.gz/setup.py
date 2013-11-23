#  from setuptools import setup, find_packages
# from distutils.core import setup
from setuptools import setup
from etmQt.v import version
# import etmQt
import glob

# Hack to avoid requiring python for versions >= 3.2
# which breaks installation under os x mavericks
import sys
if sys.version_info >= (3, 2):
    REQUIRES = ["python-dateutil>=1.5", "PyYaml>=3.10", "icalendar>=3.5"],
else:
    REQUIRES = ["python>=2.7,<3.0", "python-dateutil>=1.5", "PyYaml>=3.10",
                "icalendar>=3.5"],

setup(
    name='etm_qt',
    version=version,
    zip_safe=False,
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
        'Topic :: Office/Business :: Scheduling'],
    packages=['etmQt'],
    scripts=['etm_qt'],
    install_requires=REQUIRES,
    package_data={
        'etmQt': ['icons/*', '*.html', 'version.txt', 'CHANGES',
                  'applications/etm_qt.desktop', 'etm_qt.1', 'etm_qt.xpm'],
        'etmQt/help': ['help/*.html'],
        'etmQt/images': ['images/*.png'],
        'etmQt/help/images': ['help/images/*.png'],
        'etmQt/language': ['language/*.html', 'language/*.qm'],
        'etmQt/language/images': ['language/images/*.png'],
        'etmQt/icons': ['icons/*']},
    data_files=[
        ('share/doc/etm_qt', ['etmQt/version.txt', 'etmQt/CHANGES',
                              'etmQt/INSTALL.html']),
        ('share/man/man1', ['etmQt/etm_qt.1']),
        ('share/pixmaps', ['etmQt/etm_qt.xpm']),
        ('share/applications', ['etmQt/applications/etm_qt.desktop']),
        ('share/icons/etm_qt', glob.glob('etmQt/icons/*.png')),
        ('share/doc/etm_qt/help', glob.glob('etmQt/help/*.html')),
        ('share/doc/etm_qt/help/images', glob.glob('etmQt/images/*.png')),
        ('share/doc/etm_qt/help/images', glob.glob('etmQt/help/images/*.png')),
        ('share/doc/etm_qt/language', glob.glob('etmQt/language/*.html')),
        ('share/doc/etm_qt/language/images',
            glob.glob('etmQt/language/images/*.png'))]
)
