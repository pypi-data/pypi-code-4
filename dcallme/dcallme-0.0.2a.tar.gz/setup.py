import setuptools

setuptools.setup(
    name="dcallme",
    version="0.0.2a",
    author="Stas D",
    author_email="st@dcall.me",
    url="https://github.com/swight/dcallme",
    license="BSD",
    description="dCall.me IP-PBX Cloud Service client",
    keywords="dcallme ip pbx cloud service client",
    packages=setuptools.find_packages(),
    install_requires=['requests==1.2.0'],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    tests_require=['mock==1.0.1'],
    test_suite='tests.runtests.runtests',
)
