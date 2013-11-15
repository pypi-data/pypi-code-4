from distutils.core import setup

packages=[
    'sdipy',
]
    
requiredPackages=[]

setup(
    name='SDIPy',
    version='1.0',
    author='Charles Fracchia',
    author_email='charlesfracchia@gmail.com',
    packages=packages,
    scripts=[],
    url='https://github.com/charlesfracchia/SDIPy',
    license='LICENSE',
    description='Python library for the Sensor Data Interoperability Protocol',
    long_description=open('README').read(),
    requires=requiredPackages,
    provides=packages,
)
