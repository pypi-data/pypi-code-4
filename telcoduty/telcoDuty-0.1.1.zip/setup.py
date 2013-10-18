from setuptools import setup, find_packages
setup(
    name="telcoDuty",
    version="0.1.1",
    entry_points={
        'console_scripts': [
            'telcoDuty = telcoDuty.telcoDuty:main',
            ]
    },
    packages=['telcoDuty'],
    setup_requires=['requests'],
    install_requires=['requests'],
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        'telcoDuty': ['WinSCP.com', 'WinSCP.exe']
    },
    zip_safe=False,
    author="Me",
    author_email="alexey.grachev@nordigy.ru",
    description="Telco duty routine helper",
    license="PSF",
    keywords="hello world example examples",
    url='https://pypi.python.org/simple/telcoDuty'
)
