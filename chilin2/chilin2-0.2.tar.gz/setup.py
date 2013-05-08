from distutils.core import setup

setup(
    name='chilin2',
    version='0.2',
    packages=['chilin2', 'chilin2.function_template'],
    url='',
    license='MIT',
    author='Hanfei Sun, Shenglin Mei, Qian Qin ',
    author_email='hfsun.tju@gmail.com',
    description='ChIP-seq pipeline',
    scripts = ["chilin2/ChiLin2.py"],
    requires=['jinja2','samflow','argparser'],
    package_data = {"chilin2" : ["db/ChiLinQC.db", "jinja_template/*.jinja2","db/*.txt"]}
)
