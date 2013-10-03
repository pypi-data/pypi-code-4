from distutils.core import setup
setup(
    name='kstats',
    version='0.1',
    author='Syed Ali',
    author_email='syed_a_ali@yahoo.com',
    packages=['kstats'],
    scripts=['bin/kstats'],
    url='http://pypi.python.org/pypi/kstats/',
    license='LICENSE.txt',
    description='KVM Stats.',
    long_description=open('README.txt').read(),
    install_requires=[
        "argparse >= 1.2.1",
        "python-hostlist >= 1.14",
    ],
)
