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
    name='pyschelling',
    version='0.1.0',
    description="An agent-based implementation of Schelling's segregation model",
    long_description=readme(),
    keywords='agent based Schelling segregation',
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
        'pyschelling'
    ],
    url='https://github.com/ggstuart/pyschelling.git',
    entry_points = {
        'console_scripts': [
            'pyschelling_console=pyschelling.model:main',
            'pyschelling_gui=pyschelling.GUI:main'
        ],
    }
)
