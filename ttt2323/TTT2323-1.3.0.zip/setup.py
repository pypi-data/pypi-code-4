from distutils.core import setup

setup(
    name ='TTT2323',#1. 会在pypi中显示出来，表示你的包名     2. 这个名字要是独一无二的，不然会报错。而且在pypi中是忽略大小写的。我之前
	#写的是HelloWorld.但是在pypi中有个helloworld，结果就不能注册了
    version='1.3.0',
    author='hwb',
    author_email='test@test',
    description='it can print hellp world',
    py_modules=['HelloWorld','Test'],   #空间名称,可以有多个
    )
