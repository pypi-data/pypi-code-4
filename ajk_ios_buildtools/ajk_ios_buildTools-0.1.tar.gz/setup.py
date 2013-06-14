from setuptools import setup

setup(name='ajk_ios_buildTools',
      version='0.1',
      description='for daily build,RC test...',
      url='git@github.com:wadecong/buildTools_py_ios.git',
      author='Wade Cong',
      author_email='eva0612017@126.com',
      license='MIT',
      packages=['buildTools'],
      scripts=['bin/dailyBuild','bin/getAll'],
      zip_safe=False)
