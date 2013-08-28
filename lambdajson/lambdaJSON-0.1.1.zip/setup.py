from distutils.core import setup

setup(
    name='lambdaJSON',
    version='0.1.1',
    author='Pooya Eghbali',
    author_email='persian.writer@gmail.com',
    packages=['lambdaJSON'],
    url='https://github.com/pooya-eghbali/lambdaJSON',
    license='LICENSE.txt',
    description='Serialize python standard types (tuple, bytes, dict with number keys, byte keys or tuple keys, and etc) with json',
    long_description=open('README.txt').read()
)
