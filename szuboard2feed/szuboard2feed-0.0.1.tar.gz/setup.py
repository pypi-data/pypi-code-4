from setuptools import setup

setup(
    name='szuboard2feed',
    packages=['szuboard2feed'],
    version='0.0.1',
    license="MIT License",
    install_requires=["requests", "times", "lxml", "gevent", "crszu"],
    description='Convert SZUboard (Gongwentong) to feed.',
    author='MarkNV',
    author_email='marknv1991@gmail.com',
    url='https://github.com/marknv/szuboard2feed',
    test_suite="nose.collector",
    tests_require=["nose"],
    include_package_data=True
)
