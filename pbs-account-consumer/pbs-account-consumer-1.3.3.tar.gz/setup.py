from setuptools import setup, find_packages

dependencies = (
    'Django>=1.3',
    'python-openid>=2.2.5',
)

setup(
    name='pbs-account-consumer',
    version='1.3.3',
    description='PBS UUA OpenId Consumer',
    author='PBS Core Services Team',
    author_email='PBSi-Team-Core-Services@pbs.org',
    packages=find_packages(),
    install_requires=dependencies,
    tests_require=('mock<=1.0.1', ),
    include_package_data=True
)
