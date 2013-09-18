from setuptools import setup, find_packages

setup(
    name='django-pummel',
    version='0.0.1',
    description='Django PML template tags and utils (djang-pml was taken, okay!)',
    long_description=open('README.rst', 'r').read() + open('AUTHORS.rst', 'r').read() + open('CHANGELOG.rst', 'r').read(),
    author='Praekelt Foundation',
    author_email='dev@praekeltfoundation.org',
    license='Proprietary',
    url='http://github.com/praekelt/django-pummel',
    packages=find_packages(),
    dependency_links=[
    ],
    install_requires=[
        'django',
        'lxml',
        'pytidylib',
        'BeautifulSoup>=3.0.8.1',
    ],
    tests_require=[
        'django-setuptest',
    ],
    test_suite="setuptest.setuptest.SetupTestSuite",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    zip_safe=False,
)
