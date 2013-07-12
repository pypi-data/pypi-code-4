from setuptools import setup

setup(
    name='mallard',
    version='0.1.0',
    author='Nicolas Esteves',
    author_email='hamstahguru@gmail.com',
    packages=['mallard', 'mallard.examples'],
    url='https://github.com/hamstah/mallard',
    description='Library to send events to ducksboard.com',
    install_requires=["requests==1.2.3"]
)
