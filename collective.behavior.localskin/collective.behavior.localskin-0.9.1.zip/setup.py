from setuptools import setup, find_packages

setup(
    name='collective.behavior.localskin',
    version='0.9.1',
    description='Dexterity behavior to enable a local theme skin',
    long_description=(open('README.rst').read() + '\n' +
                      open('CHANGES.rst').read()),
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Plone :: 4.3'
    ],
    keywords='',
    author='Asko Soukka',
    author_email='asko.soukka@iki.fi',
    url='https://github.com/collective/collective.behavior.localskin/',
    license='GPL',
    packages=find_packages('src', exclude=['ez_setup']),
    package_dir={'': 'src'},
    namespace_packages=['collective', 'collective.behavior'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Products.CMFCore',
        'Zope2',
        'collective.behavior.localregistry',
        'plone.app.dexterity',
        'plone.app.registry',
        'plone.behavior',
        'plone.registry',
        'plone.supermodel',
        'setuptools',
        'z3c.form',
        'zope.component',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.schema',
    ],
    extras_require={'test': [
        'plone.app.testing',
        'plone.app.robotframework',
    ]},
    entry_points='''
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    '''
)
