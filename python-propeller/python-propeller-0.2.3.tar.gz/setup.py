from distutils.core import setup
from os.path import join, dirname


def read(fname):
    with open(join(dirname(__file__), fname)) as f:
        return f.read()


setup(
    name='python-propeller',
    version='0.2.3',
    description='Pretty progress and load indicators',
    author='Thomas Einsporn, Manuel Barkhau',
    author_email='mb@nexttuesday.de, mb@nexttuesday.de',
    long_description=read("README.md"),
    license="BSD",
    url="https://github.com/mbarkhau/python-propeller",
    download_url="https://github.org/mbarkhau/python-propeller/",
    packages=['propeller'],
    keywords="progress loading indicator propeller",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries'
    ],
)

