from distutils.core import setup


with open('README.rst') as f:
    readme = f.read()


setup(
    version='0.0.2',
    name='requests-auth-mashery',
    description='Mashery authentication for requests',
    long_description=readme,
    url='https://github.com/dasevilla/requests-auth-mashery',
    author='Devin Sevilla',
    author_email='dasevilla@gmail.com',
    install_requires=['requests>=1.2.3'],
    py_modules=['requests_auth_mashery'],
    classifiers=[
    ]
)
