from distutils.core import setup

setup(
    name='easypool',
    version='1.0.4',
    packages=['easypool',],
    license='GPLv2',
    description='Module to easily create threadpools',
    long_description="""\
    easypool was created to make the creation of threadpools in Python very easy. It also supports the dynamic creation of threadpools by accepting common Python data structures, including but not limited: integers, floats, lists, dictionaries, tuples, strings and any other data structure that can be iterated. easypool can link each thread to the value of each item given to it (e.g. Inialize easypool with list [a, b, c] and thread 0 is linked to a, thread 1 is linked to b and thread 1 is linked to value c) the linked value can be sent as the first argument to the function that the thread is executing. Link threads to server addresses and create a function that remotely executes commands on the server address. """,
    author='Robert Labonte',
    author_email='rlabonte@gmail.com',
    url='https://github.com/RobertLabonte/easypool',
    download_url='https://github.com/RobertLabonte/easypool/tarball/1.0.4',
    keywords = ['threads', 'threading', 'queue', 'threadpool'],
)
