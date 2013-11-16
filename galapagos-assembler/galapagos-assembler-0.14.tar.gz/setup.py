from distutils.core import setup

setup(
    name='galapagos-assembler',
    version='0.14',
    author=u'Sigve Sebastian Farstad',
    author_email='sigvefarstad@gmail.com',
    packages=['galapagos'],
    url='http://github.com/dmpro-ytelse/galapagos-as',
    description='Assembles Galapagos assembly.',
    entry_points={
        'console_scripts': [
            'galapagos-as = galapagos:main'
        ]
    }
)
