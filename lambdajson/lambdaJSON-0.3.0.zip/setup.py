from distutils.core import setup

setup(
    name='lambdaJSON',
    version='0.3.0',
    author='Pooya Eghbali',
    author_email='persian.writer@gmail.com',
    packages=['lambdaJSON'],
    url='https://github.com/pooya-eghbali/lambdaJSON',
    license='LGPLv3',
    description="""Use json to serialize unsupported python types (and many more including functions, classes, exceptions, etc). Changes: A lot of improvements.""",
    long_description=open('README.txt').read(),
    classifiers= ['Intended Audience :: Developers',
                  'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
                  'Operating System :: OS Independent',
                  'Programming Language :: Python :: 2',
                  'Programming Language :: Python :: 3'],
    keywords = 'json, serialization, serialize, pickle, marshal',
    platforms= ['Any']
)
