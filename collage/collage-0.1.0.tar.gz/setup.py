from setuptools import setup

setup(
    name='collage',
    version='0.1.0',
    author='John Bywater',
    author_email='jabywater@gmail.com',
    packages=['collage', 'collage.test'],
    scripts=['bin/collage-create'],
    url='http://pypi.python.org/pypi/collage/',
    license='LICENSE.txt',
    description='Creates collages of miniature images that resemble original downloaded from Google Images.',
    long_description=open('README.txt').read(),
    install_requires= [
        "Pillow",
        "numpy",
    ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Games/Entertainment',
    ],
)
