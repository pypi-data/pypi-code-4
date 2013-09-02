from distutils.core import setup

setup(
    description='College GPA Calculator',
    author='Alex Kang',
    url='https://pypi.python.org/pypi?:action=display&name=GradeBot',
    download_url='https://pypi.python.org/pypi?:action=display&name=GradeBot',
    license='GPL',
    author_email='akang95@gmail.com',
    version='0.1.6',
    install_requires=['nose'],
    packages=['gradebot', 'gradebot.test'],
    scripts=['bin/gradebot'],
    name='GradeBot'
)
