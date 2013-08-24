from distutils.core import setup

setup(
    description = 'College GPA Calculator',
    author = 'Alex Kang',
    url = 'https://pypi.python.org/pypi?:action=display&name=GradeBot&version=0.1.0',
    download_url = 'https://pypi.python.org/pypi?:action=display&name=GradeBot&version=0.1.0',
    license = 'LICENSE.txt',
    author_email = 'akang95@gmail.com',
    version = '0.1.2',
    install_requires = ['nose'],
    packages = ['gradebot', 'gradebot.test'],
    scripts = ['bin/gradebot'],
    name = 'GradeBot'
)
