from setuptools import find_packages
from setuptools import setup


setup(
    name='plone.formwidget.datetime',
    version='1.0',
    description="Datetime widgets for Plone",
    long_description=open("README.rst").read() + "\n" +
        open("CHANGES.rst").read(),
    # Get more strings from
    # http://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
    ],
    keywords='plone date time datetime event widget archetypes z3c.form',
    author='Plone Foundation',
    author_email='plone-developers@lists.sourceforge.net',
    url='https://github.com/plone/plone.formwidget.datetime',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['plone', 'plone.formwidget'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'DateTime',
        'Products.CMFPlone',
        'plone.app.jquerytools',
        'pytz',
        'zope.i18nmessageid',
        'zope.interface',
    ],
    extras_require=dict(
        z3cform=[
            'z3c.form',
            'zope.component',
            'zope.schema',
        ],
        archetypes=[
            'Products.Archetypes',
            'Products.CMFCore',
            'Zope2',
        ],
        test=[
            'plone.formwidget.datetime[archetypes, z3cform]',
            'Products.ATContentTypes',
            'Products.GenericSetup',
            'lxml',
            'mock',
            'plone.app.testing',
            'plone.testing',
            'unittest2',
            'zc.buildout',
            'zope.app.testing',
            'zope.configuration',
            'zope.security',
            'zope.testing',
        ],
      ),
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
)
