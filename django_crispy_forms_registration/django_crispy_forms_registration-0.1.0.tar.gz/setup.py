from setuptools import setup

setup(
    name='django_crispy_forms_registration',
    version='0.1.0',
    author='Vijay Khemlani',
    author_email='vkhemlan@gmail.com',
    packages=[
        'crispy_forms_registration',
        'crispy_forms_registration.forms',
    ],
    scripts=[],
    url='https://github.com/SoloTodo/django_crispy_forms_registration',
    license='LICENSE.txt',
    description='Library that merges Django auth, registration, and crispy',
    long_description=open('README.rst').read(),
    install_requires=[
        'Django>=1.4,<1.5',
        'django-registration>=1.0',
        'django-crispy-forms>=1.4.0'
    ],
)
