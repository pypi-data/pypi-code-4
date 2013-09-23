from distutils.core import setup

setup(
    name='django-panacea',
    version='0.1.2',
    description='Django caching middleware for NGINX httpredis module. Based on django-cacheops',
    author='klem4',
    author_email='useperlordie@gmail.com',
    url='https://github.com/klem4/panacea',
    packages=[
        'panacea',
        'panacea.management',
        'panacea.management.commands'
    ],
    package_data={
        '': ['templates/*.html']
    }
)