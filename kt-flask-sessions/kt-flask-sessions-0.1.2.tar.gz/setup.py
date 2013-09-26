from setuptools import setup

setup(
    author='Quinlan Pfiffer',
    author_email='qpfiffer@gmail.com',
    url='https://github.com/qpfiffer/KyotoTycoonFlaskSessions',
    name='kt-flask-sessions',
    description='Kyoto Tycoon backed sessions for Flask',
    version='0.1.2',
    license='BSD',
    keywords='Kyoto Tycoon, Flask',
    packages=['ktsessions'],
    zip_safe=False,
    install_requires = [
        "python-kyototycoon",
        "werkzeug",
        "flask"
    ]
)
