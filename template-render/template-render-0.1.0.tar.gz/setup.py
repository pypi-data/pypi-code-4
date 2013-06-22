from distutils.core import setup, Command

class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import sys,subprocess
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)

setup(
    name='template-render',
    version='0.1.0',
    author='Mark Stillwell',
    author_email='marklee@fortawesome.org',
    packages=['templaterender', 'templaterender.test'],
    scripts=['bin/template-render'],
    url='http://pypi.python.org/pypi/template-render/',
    license='LICENSE.txt',
    description='Template Rendering Scripts',
    long_description=open('README.txt').read(),
    keywords='',
    classifiers=[
      'Development Status :: 1 - Planning',
      'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    ],
    cmdclass = {'test': PyTest},
)
