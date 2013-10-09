from distutils.core import setup

setup(
    name='WikiUtils',
    version='1.0.0-rc1',
    author='Juergen Jakobitsch',
    author_email='office@turnguard.com',
    packages=['python','python.turnguard','python.turnguard.com'],
    py_modules=['wikiutils'],
    url='http://python.turnguard.com',
    license='LICENSE.txt',
    description='WikiUtils',
    long_description=open('README.txt').read(),
    install_requires=[
        "urllib3 >= 1.7.1",
        "lxml == 2.3.4",
    ],
)
