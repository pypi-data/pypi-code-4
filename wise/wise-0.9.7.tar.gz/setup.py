from distutils.core import setup

setup(
    name='wise',
    version='0.9.7',
    author='Henrik Brink',
    author_email='henrik@wise.io',
    packages=['wise'],
    url='https://wise.io',
    license='LICENSE.txt',
    description='Client library for the wise.io machine-learning service.',
    requires=["requests (>=1.2.0)", "pandas"],
    scripts = [
        'scripts/wise'
    ]
)
