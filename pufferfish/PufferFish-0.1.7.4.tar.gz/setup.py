from setuptools import setup

setup(
    name='PufferFish',
    version='0.1.7.4',
    author='Giacomo Bagnoli',
    author_email='info@asidev.com',
    packages=['pufferfish', 'pufferfish.tests', 'pufferfish.tests.model'],
    include_package_data = True,
    url='http://code.asidev.net/pufferfish/',
    license='LICENSE.txt',
    description='SQLAlchemy session extension',
    long_description=open('README.txt').read(),
    install_requires = [
        "SQLAlchemy >= 0.6.0",
        "Elixir >= 0.7.1",
        "python-magic >= 0.3.1"
    ],
    test_suite = 'nose.collector',
    tests_require = [ "Nose", "coverage" ],
    classifiers  = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Database :: Front-Ends",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
