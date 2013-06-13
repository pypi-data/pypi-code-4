from distutils.core import setup

setup(
    name='resumen-credicoop',
    version='0.0.2',
    author='Alberto Paparelli (a.k.a. carpediem)',
    author_email='alberto@paparelli.com.ar',
    packages=['credicoop'],
    scripts=['resumen-credicoop'],
    url='https://github.com/carpe-diem/resumen-credicoop/',
    license='GPL-3',
    description='Resumen banco Credicoop.',
    long_description="Resumen banco credicoop",
    install_requires=[
        "lxml==3.2.1",
        "pdfminer==20110515",
    ],
)
