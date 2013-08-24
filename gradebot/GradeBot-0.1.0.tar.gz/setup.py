from distutils.core import setup

setup(
    description = 'College GPA Calculator',
    author = 'Alex Kang',
    url = '',
    download_url = '',
    author_email = 'akang95@gmail.com',
    version = '0.1.0',
    install_requires = ['nose'],
    packages = ['gradebot'],
    scripts = ['bin/gradebot'],
    name = 'GradeBot'
)
