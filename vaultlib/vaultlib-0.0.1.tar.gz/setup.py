try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


requires = [
    'rsa==3.1.1',
    'pycouchdb==1.6'
]


setup(
    name='vaultlib',
    description='vault library.',
    long_description=(
        '%s\n\n%s' % (
            open('README.md').read(),
            open('CHANGELOG.md').read()
        )
    ),
    version=open('VERSION').read().strip(),
    author='Alex Ethier',
    author_email='vault@fx-tools.com',
    license=open('LICENSE').read(),
    url='',
    package_dir={'vaultlib': 'src'},
    packages=[
        'vaultlib',
        'vaultlib.vault'
    ],
    install_requires=requires,
    scripts = ['src/bin/vault-cli']
)
