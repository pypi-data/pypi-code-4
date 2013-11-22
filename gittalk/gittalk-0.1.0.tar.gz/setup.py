from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='gittalk',
    version='0.1.0',
    url='https://github.com/kqdtran/gittalk',
    author='Khoa Tran',
    author_email='khoatran@berkeley.edu',
    keywords=('git', 'audio', 'gittalk'),
    description=('talk with git'),
    long_description=readme(),
    license='MIT',
    packages=['gittalk'],
    install_requires=[
        'pyttsx>=1.1',
    ],
    scripts=[
        'bin/gittalk'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2',
    ],
    include_package_data=True,
    zip_safe=False
)