from distutils.core import setup

setup(
    name='VTIXyProxy',
    version='1.0.2',
    packages=['vtixy_proxy',],
    license='LICENSE.txt',
    description='Web services for applications of VTIX.RU clients',
    long_description=open('README.txt').read(),
    install_requires=[
        "django-rest-framework-proxy >= 1.1.0",
    ],
)