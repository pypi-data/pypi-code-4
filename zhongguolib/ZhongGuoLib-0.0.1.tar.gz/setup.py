from distutils.core import setup

setup(
    name='ZhongGuoLib',
    version='0.0.1',
    author='Alexander Stefanov',
    author_email='alexander.stefanov@lulin.bg',
    packages=['zhongguolib', 'zhongguolib.test'],
    scripts=[''],
    url='http://pypi.python.org/pypi/zhongguolib/',
    license='LICENSE.txt',
    description='Useful chinese language stuff.',
    long_description=open('README.txt').read(),
)