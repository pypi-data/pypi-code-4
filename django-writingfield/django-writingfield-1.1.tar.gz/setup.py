import os
from distutils.core import setup
from writingfield import get_version

root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)

setup(
    name='django-writingfield',
    version=get_version(),
    license='BSD 3 Clause',
    description='A fullscreen textfield widget for Django',
    long_description=open('README.md').read(),
    author='Jamie Curle',
    author_email='jamie@curle.io',
    url='https://github.com/jamiecurle/django-writingfield',
    package_data={
        'writingfield' : [
            'static/writingfield/*.js',
            'static/writingfield/*.css',
        ],
    },
    packages=[
        'writingfield',
    ],)
