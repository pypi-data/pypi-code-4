from distutils.core import setup

setup(
    name='piper',
    version='0.1.0',
    description='A shell-like object pipeline',
    long_description=open("README.rst").read(),
    author='Anton Backer',
    author_email='olegov@gmail.com',
    url='http://www.github.com/staticshock/piper',
    py_modules=['piper'],
    license='ISC',
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
    ),
)
