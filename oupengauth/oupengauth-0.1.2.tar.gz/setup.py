from setuptools import setup, find_packages


VERSION = '0.1.2'

setup(name='oupengauth',
        version=VERSION, 
        author='kula',
        author_email='kulasama@gmail.com',
        url='http://oupeng.com',
        description='A oauth client library.',
        packages = find_packages(),
        long_description="""
support sns: sina,taobao,qq,renren
        """,

        package_data={'oupengauth': ['*.txt']},
        )
