from distutils.core import setup

setup(
    name='proctorserv_api',
    version='0.2',
    packages=['proctorserv',],
    url='https://github.com/ProctorCam/proctorserv-api-python',
    author='Jide Fajobi',
    author_email='Jide@ProctorCam.com',
    license='Apache V2.0',
    install_requires=[
          'requests',
          ],
)