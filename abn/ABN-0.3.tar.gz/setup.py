from setuptools import setup

setup(
    name='ABN',
    version='0.3',
    py_modules=['abn'],
    test_suite='tests',
    license='Apache 2.0',
    description='Validate Australian Business Numbers.',
    long_description=open('README').read(),
    url='https://gitorious.org/abn',
    author='Ben Sturmfels',
    author_email='ben@sturm.com.au',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Office/Business',
    ],
)
