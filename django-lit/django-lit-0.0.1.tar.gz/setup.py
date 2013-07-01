from setuptools import setup
import lit

setup(name='django-lit',
    version=lit.__version__,
    description='',
    author='20tab srl: Raffaele Colace - Gabriele Giaccari',
    author_email='info@20tab.com',
    url='https://github.com/20tab/django-lit',
    license='MIT License',
    platforms=['OS Independent'],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    install_requires=[
        'Django >=1.5',
    ],
    packages=['lit',],
    include_package_data=True,
    zip_safe=False,
    package_data = {
        '': ['*.html', '*.css', '*.js', '*.gif', '*.png',],
    }
)