from distutils.core import setup

setup(
    name='glespy',
    version='0.1.2',
    packages=['glespy', 'glespy.test', 'glespy.tools', 'glespy.tools.test', 'glespy.test_data'],
    url='',
    license='no license yet...',
    author='yarnaid',
    author_email='yarnaid@gmail.com',
    description='bindings for GLESP',
    keywords='GLESP bindings',
    long_description=open('README.md').read(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
        "Intended Audience :: Science/Research",
        "License :: Freeware",
        "Natural Language :: Russian",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2",
        "Topic :: Scientific/Engineering :: Astronomy",
    ],
)
