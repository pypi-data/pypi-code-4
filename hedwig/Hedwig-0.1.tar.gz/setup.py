from setuptools import find_packages, setup


with open('README.rst') as f:
    long_description = f.read()


setup(
    name='Hedwig',
    version='0.1',
    url='https://github.com/kimjayd/hedwig',
    license='MIT',
    author='Hyunjun Kim',
    author_email='kim@hyunjun.kr',
    description='django.core.mail without django.',
    long_description=long_description,
    packages=find_packages(),
    platforms='any',
)
