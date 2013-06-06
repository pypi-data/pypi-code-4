from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

def readme():
    with open('README.md') as f:
        return f.read()

setup(ext_modules=[Extension("BayesRedis", ["BayesRedis/__init__.c"])],
      cmdclass={'build_ext': build_ext},
      name='bayesredis',
      version='1.0.0',
      description='A Simple Naive Bayes Classifier in Python',
      long_description=readme(),
      keywords='bayes naive classifier redis cython',
      url='https://github.com/tistaharahap/python-bayes-redis',
      author='Batista Harahap',
      author_email='batista@bango29.com',
      license='MIT',
      packages=['BayesRedis'],
      install_requires=['redis'],
      zip_safe=False)
