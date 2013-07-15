from distutils.core import setup

setup(
    name='PushFactory',
    version='0.1.1',
    author='Jochem Oosterveen',
    author_email='jochem@oosterveen.net',
    packages=['push'],
    description='Generic interface for push messages',
    long_description=open('README.txt').read(),
    install_requires=[
        "pyapns >= 0.4.0",
    ],
)
