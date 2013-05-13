from setuptools import setup, find_packages

f=open("README.md")

setup(
    name='pynomenklatura',
    version='0.3',
    description="Client library for nomenklatura, make record linkages on the web.",
    long_description="\n".join(f),
    classifiers=[
        ],
    keywords='data mapping identity linkage record',
    author='Open Knowledge Foundation',
    author_email='info@okfn.org',
    url='http://github.com/okfn/nomenklatura-client',
    license='AGPLv3',
    py_modules=['nomenklatura'],
    zip_safe=False,
    install_requires=[
        "requests>=1.2"
    ],
    tests_require=[],
    entry_points=\
    """ """,
)
