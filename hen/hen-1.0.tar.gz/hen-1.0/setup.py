from setuptools import setup, find_packages
setup(
    name = "hen",
    version = "1.0",
    scripts = ['hen'],
    #packages = find_packages(),
    author = "Sergey Kirillov",
    author_email = "sergey.kirillov@gmail.com",
    description = "Process runner inspired by foreman",
    url = "http://bitbucket.org/rushman/hen/",
    install_requires = ['termcolor', 'pyyaml']
)
