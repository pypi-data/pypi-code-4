

from distutils.core import setup

setup(
    name='Hamilton',
    version='0.1.0',
    author='Senne Van Baelen',
    author_email='senne_vb@hotmail.com',
    packages=['Hamilton','Hamilton.Interface','Hamilton.Interface.Examples'],
    #scripts=[''],
    url='http://pypi.python.org/pypi/Hamilton/',
    license='LICENSE.txt',
    description='Visualize and control mechanic systems through solving these systems with Hamiltonian mechanics.',
    long_description=open('README.txt').read(),
    
)


