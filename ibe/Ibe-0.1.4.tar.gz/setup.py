from distutils.core import setup

setup(
    name='Ibe',
    version=open('CHANGES.txt').read().split()[0],
    author='Lucas Pandolfo Perin / Lucas Boppre Niehues',
    author_email='lucasperin@gmail.com / lucasboppre@gmail.com',
    packages=['ibe'],
    url='http://pypi.python.org/pypi/Ibe/',
    license='LICENSE.txt',
    description='Simple IBE library - This might be the start of something really neat!',
    long_description=open('README.rst').read(),

    scripts=['bin/pkg_server.py','bin/install_pypbc.sh'],
    install_requires=[
        "crypto",
    ],

    classifiers=[
        "Development Status :: 1 - Planning",
        "Topic :: Security :: Cryptography",
        "License :: OSI Approved :: MIT License",
    ],
)