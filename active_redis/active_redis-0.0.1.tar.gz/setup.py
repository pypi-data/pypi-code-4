from setuptools import setup

setup(
    name='active_redis',
    version='0.0.1',
    scripts=[],
    install_requires = ['redis'],
    packages=['active_redis'],
    author = 'Samuel Sanchez',
    author_email = 'samuel@pagedegeek.com',
    description = 'Simple ActiveRecord pattern for Redis',
    long_description=open('README').read(),
    keywords = 'Redis ActiveRecord',
    url = 'http://github.com/PagedeGeek/active_redis'
)

