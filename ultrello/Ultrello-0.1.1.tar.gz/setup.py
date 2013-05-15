from distutils.core import setup

setup(
    name='Ultrello',
    version='0.1.1',
    author='Luke Snyder',
    author_email='lsbomber1@gmail.com.',
    packages=['ultrello', 'ultrello.test'],
    url='http://pypi.python.org/pypi/Ultrello/',
    description='Trello API information retrieval for users.',
    long_description=open('README.txt').read(),
    install_requires=[
        "requests == 1.2.0",
    ],
)