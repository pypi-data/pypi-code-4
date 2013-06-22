from setuptools import setup

try:
    import pygtk
except ImportError:
    print 'You need to install pyGTK to use this'
    exit()

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='pygameoflife',
    version='0.1.0',
    description="An agent-based implementation of Conway's Game of Life",
    long_description=readme(),
    keywords='agent based Conway game of life',
    author='Graeme Stuart',
    author_email='ggstuart@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 2.7',
        'Topic :: Games/Entertainment :: Arcade',
        'Environment :: X11 Applications :: GTK',
    ],
    license='LICENSE.txt',
    install_requires=[
        'pyagents'
    ],
    packages=[
        'pygameoflife'
    ],
    url='https://github.com/ggstuart/pygameoflife.git',
    entry_points = {
        'console_scripts': [
            'pygameoflife_console=pygameoflife.model:main',
            'pygameoflife_gui=pygameoflife.GUI:main'
        ],
    }
)
