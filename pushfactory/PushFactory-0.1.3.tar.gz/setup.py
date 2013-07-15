from distutils.core import setup

setup(
    name='PushFactory',
    version='0.1.3',
    author='Jochem Oosterveen',
    author_email='jochem@oosterveen.net',
    packages=['push'],
    description='Generic interface for push messages',
    long_description=open('README.txt').read(),
    install_requires=[
        "pyapns >= 0.4.0",
        "python-gcm==0.1.4",
    ],
)
