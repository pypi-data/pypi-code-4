from setuptools import setup


if __name__ == '__main__':
  setup(
    name='Flask-Upstatic',
    version='0.0.2',
    description="Opinionated library for working with CDNs in Flask.",
    long_description=open('README.rst').read(),
    author='Mark Steve Samson',
    author_email='marksteve@insynchq.com',
    url='https://github.com/insynchq/flask-upstatic',
    license='MIT',
    py_modules=['flask_upstatic'],
    install_requires=[
      'boto',
    ]
  )
