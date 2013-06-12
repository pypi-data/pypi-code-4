from distutils.core import setup

setup(
    name='resumen-credicoop',
    version='0.0.1',
    author='Alberto Paparelli (a.k.a. carpediem)',
    author_email='alberto@paparelli.com.ar',
    packages=['credicoop'],
    scripts=['bin/resumen-credicoop.py'],
    url='https://github.com/carpe-diem/resumen-credicoop/',
    license='GPL-3',
    description='Resumen banco Credicoop.',
    long_description="Resumen banco credicoop",
    install_requires=[
        "beautifulsoup4==4.2.0",
        "lxml==3.2.1",
        "pdfminer==20110515",
    ],
)
