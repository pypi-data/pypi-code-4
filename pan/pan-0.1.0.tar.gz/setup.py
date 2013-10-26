from distutils.core import setup

setup(
    name='pan',
    version='0.1.0',
    author='Ben Whalley',
    author_email='benwhalley@gmail.com',
    packages=['pan'],
    scripts=[
        'bin/pan', 
        "bin/stata.py", 
        "bin/instructor.py"
    ],
    url='http://pypi.python.org/pypi/pan/',
    license='LICENSE.txt',
    description='Command line tool with sane defaults for building academic articles from markdown using pandoc.',
    long_description=open('README.txt').read(),
    install_requires=[
        "PyYAML>=3.10",
        "clint>=0.3.1",
        "envoy>=0.0.2",
        "statpipe"
    ],
)