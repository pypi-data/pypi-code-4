try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='sonnet',
    version='0.1.2',
    author='David Michael Brown',
    author_email='davidmichaelbrown1@gmail.com',
    packages=['sonnet', ],
    url='myurl',
    license='MIT',
    long_description=open('README.rst').read(),
    install_requires=['networkx==1.8.1'],
    keywords='networkx json graph javascript D3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
    ]
)
