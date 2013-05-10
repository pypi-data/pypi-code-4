from setuptools import setup, find_packages

setup(
    name='pip-crate',
    author='Pedro Palhares',
    author_email='pedrospdc@gmail.com',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'pip',
    ],
    description='Simple pip wrapper that uses crate.io repository for better speed.',
    url='https://github.com/pedrospdc/pip-crate',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    entry_points=dict(console_scripts=['pip-crate=pip_crate:main']),
)