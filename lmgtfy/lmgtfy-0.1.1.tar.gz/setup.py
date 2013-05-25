from setuptools import setup

with open('README.md') as file:
    long_description = file.read()

setup(
    name='lmgtfy',
    description='Let me Google that for you',
    version='0.1.1',
    packages=['lmgtfy'],
    long_description=long_description,
    license='MIT',
    author='Akash Kothawale',
    platforms='Linux',
    author_email='io@decached.com',
    install_requires='requests>=1.2.0',
    entry_points={'console_scripts': ['lmgtfy = lmgtfy.run:command_line_runner']},
)
