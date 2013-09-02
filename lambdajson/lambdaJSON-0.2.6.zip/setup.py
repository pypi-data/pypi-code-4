from distutils.core import setup

setup(
    name='lambdaJSON',
    version='0.2.6',
    author='Pooya Eghbali',
    author_email='persian.writer@gmail.com',
    packages=['lambdaJSON'],
    url='https://github.com/pooya-eghbali/lambdaJSON',
    license='LGPLv3',
    description="""Serialize python standard types (function, tuple, set, frozenset, complex, range, bytes, 
                   dict with number keys, byte keys or tuple keys, and etc) with json. 
                   No dependencies, just needs json lib (or other json libraries). --Changes: 
                   Fixed a compatibility issue.""",
    long_description=open('README.txt').read(),
    classifiers= ['Intended Audience :: Developers',
                  'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
                  'Operating System :: OS Independent',
                  'Programming Language :: Python :: 2',
                  'Programming Language :: Python :: 3'],
    keywords = 'json, serialization, serialize, pickle, marshal',
    platforms= ['Any']
)
