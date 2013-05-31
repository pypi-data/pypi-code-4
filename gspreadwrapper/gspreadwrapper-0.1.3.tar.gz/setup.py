from distutils.core import setup

setup(
    name='gspreadwrapper',
    version='0.1.3',
    packages=['gspreadwrapper',],
    author = 'david.rossellat',
    author_email = 'david.rossellat@gmail.com',
    url = 'http://about.me/david_rossellat',
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    description='mostly having fun with google spreadsheets',
    install_requires=[
        "gspread >= 0.0.15",

    ],
)