from distutils.core import setup
setup(
    name='relaxxapi',
    packages=['relaxxapi'],
    version='0.2.2',
    description='A Wrapper around the RelaxxPlayer MPD Web Interface',
    author='Felix Richter',
    license='WTFPL',
    author_email='pypi@syntax-fehler.de',
    url='https://github.com/makefu/relaxxapi',
    install_requires = ['requests'],
#    download_url='https://github.com/makefu/relaxxapi/tarball/0.1',
    keywords=['relaxxplayer', 'api'],
)
