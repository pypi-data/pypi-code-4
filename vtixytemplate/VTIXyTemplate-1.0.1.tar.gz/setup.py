from distutils.core import setup

setup(
    name='VTIXyTemplate',
    version=__import__('vtixy_template').__version__,
    packages=['vtixy_template',],
    package_data={
        'vtixy_template': [
            'fonts/*'
        ]
    },
    include_package_data=True,
    license='LICENSE.txt',
    description='PDF Ticket generator for web applications of VTIX.RU clients',
    long_description=open('README.txt').read(),
    install_requires=[
        'django', 'slumber', 'reportlab', 'pyPdf',
    ],
)