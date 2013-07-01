from distutils.core import setup

setup(
    name='indy',
    version='0.1',
    packages=['indy', ],
    long_description=('Interactive command-line fuzzy file search, based off '
                      'how Ctrl-P works in Sublime Text'),
    license='GNU',
    entry_points={
        'console_scripts': ['indy = indy:main']
    },
    install_requires=[]
)
