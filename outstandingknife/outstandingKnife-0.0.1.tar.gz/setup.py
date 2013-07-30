from distutils.core import setup

setup(
    name='outstandingKnife',
    version='0.0.1',
    author='Michael Imelfort',
    author_email='mike@mikeimelfort.com',
    packages=['outstandingknife', 'outstandingknife.test'],
    scripts=['bin/outstandingKnife'],
    url='http://pypi.python.org/pypi/outstandingKnife/',
    license='GPLv3',
    description='outstandingKnife',
    long_description=open('README.md').read(),
    install_requires=[],
)
