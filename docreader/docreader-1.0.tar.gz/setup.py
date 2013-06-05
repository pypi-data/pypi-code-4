from distutils.core import setup

setup(
    name='docreader',
    version='1.0',
    packages=['docreader',],
    license='MIT License',
    url='https://github.com/CBWhiz/docreader',
    description="A better csv.DictReader (supporting UTF-8 and type conversion)",
    long_description=open('README.txt').read(),
    keywords='csv dictreader docreader',
    author='CBWhiz',
    author_email='CBWhiz@gmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Development Status :: 7 - Inactive',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
