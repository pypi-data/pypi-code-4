from distutils.core import setup

setup(
    name='django-i18n-model',
    version='0.0.7',
    packages=['i18n_model', 'i18n_model.templatetags'],
    license='BSD',
    author='Hajime Yamasaki Vukelic',
    author_email='hajim@7carrots.com',
    description='Translations for Django models',
    url='https://bitbucket.org/7carrots/django-i18n-model',
    download_url='https://bitbucket.org/7carrots/django-i18n-model/downloads',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
    ]
)