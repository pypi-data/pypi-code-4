from distutils.core import setup

setup(
    name='coinbase',
    version='0.0.1',
    packages=['coinbase', 'coinbase.models'],
    url='http://www.paywithair.com/libraries',
    license='MIT',
    author='George Sibble',
    author_email='george.sibble@gmail.com',
    description='Integration Library for the Coinbase API',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ],
    install_requires=[
        'Flask>=0.9',
        'httplib2>=0.8',
        'requests>=1.1.0',
        'oauth2client>=1.1'
        ]
)
