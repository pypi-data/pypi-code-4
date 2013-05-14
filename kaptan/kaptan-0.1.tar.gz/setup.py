from distutils.core import setup

setup(
    name='kaptan',
    version='0.1',
    packages=['kaptan', 'kaptan.handlers'],
    url='http://github.com/emre/kaptan',
    license='MIT',
    author='Emre Yilmaz',
    author_email='mail@emreyilmaz.me',
    description='Configuration Manager',
    requires=open('requirements.txt').readlines(),
)
