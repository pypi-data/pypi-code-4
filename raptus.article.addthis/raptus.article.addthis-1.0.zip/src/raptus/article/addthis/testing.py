from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

import raptus.article.addthis


RAPTUS_ARTICLE_ADDTHIS = PloneWithPackageLayer(
    zcml_package=raptus.article.addthis,
    zcml_filename='testing.zcml',
    gs_profile_id='raptus.article.addthis:testing',
    name="RAPTUS_ARTICLE_ADDTHIS")

RAPTUS_ARTICLE_ADDTHIS_INTEGRATION = IntegrationTesting(
    bases=(RAPTUS_ARTICLE_ADDTHIS, ),
    name="RAPTUS_ARTICLE_ADDTHIS_INTEGRATION")

RAPTUS_ARTICLE_ADDTHIS_FUNCTIONAL = FunctionalTesting(
    bases=(RAPTUS_ARTICLE_ADDTHIS, ),
    name="RAPTUS_ARTICLE_ADDTHIS_FUNCTIONAL")
