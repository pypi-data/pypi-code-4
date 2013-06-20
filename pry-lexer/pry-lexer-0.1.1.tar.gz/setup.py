from setuptools import setup

setup(
    name='pry-lexer',
    version='0.1.1',
    description="A pygments lexer for pry sessions",
    author="Conrad Irwin",
    author_email="me@cirw.in",
    packages=["pry_lexer"],
    url='https://github.com/ConradIrwin/pry-lexer',
    install_requires=['pygments'],
    entry_points='''[pygments.lexers]
prylexer = pry_lexer:PryLexer
'''
)
