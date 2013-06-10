from distutils.core import setup

setup(
    name='NMRPySchedule',
    version='0.0.1',
    packages=['nmrpyschedule', 'nmrpyschedule.format', 
              'nmrpyschedule.generator'],
    license='MIT',
    author='Matt Fenwick',
    author_email='mfenwick100@gmail.com',
    url='https://github.com/mattfenwick/NMRPySchedule',
    description='a library for building non-uniform NMR sample schedules'
)