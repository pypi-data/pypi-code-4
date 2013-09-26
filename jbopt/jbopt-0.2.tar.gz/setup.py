from distutils.core import setup

setup(
    name='jbopt',
    version='0.2',
    author='Johannes Buchner',
    author_email='buchner.johannes@gmx.at',
    packages=['jbopt'],
    scripts=[],
    url='http://johannesbuchner.github.io/jbopt/',
    license='LICENSE.txt',
    description='Parameter space exploration toolbox',
    install_requires=[
        "scipy>=0.7.0",
    ],
)

