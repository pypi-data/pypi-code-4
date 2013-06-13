from setuptools import setup

setup(
    name='amptrac',
    version='0.1',
    url='https://github.com/tomprince/amptrac',
    description="Client for twisted's amp interface to trac",
    license='MIT',
    author='Tom Prince',
    author_email='tom.prince@ualberta.net',
    packages=['amptrac', 'amptrac.test'],
    install_requires=[
        'twisted >= 13.0.0',
        'treq',
    ],
    zip_safe=False,
)
