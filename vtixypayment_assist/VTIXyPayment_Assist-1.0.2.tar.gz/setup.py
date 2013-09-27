from distutils.core import setup

setup(
    name='VTIXyPayment_Assist',
    version=__import__('vtixy_payment_assist').__version__,
    packages=['vtixy_payment_assist',],
    package_data={
        'vtixy_payment_assist': [
            'templates/*'
        ]
    },
    include_package_data=True,
    license='LICENSE.txt',
    description='Payment gate for web applications of VTIX.RU clients',
    long_description=open('README.txt').read(),
    zip_safe=False,
    install_requires=[
        'django', 'slumber',
    ],
)