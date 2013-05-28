# -*- coding: utf-8 -*-
from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

import collective.languagemovefolders

languagemovefolders = PloneWithPackageLayer(
        zcml_filename="configure.zcml",
        zcml_package=collective.languagemovefolders,
        additional_z2_products=('Products.LinguaPlone',),
        gs_profile_id='collective.languagemovefolders:default',
        name="languagemovefolders")

languagemovefolders_INTEGRATION = IntegrationTesting(
                bases=(languagemovefolders,), name="languagemovefolders_INTEGRATION")

languagemovefolders_FUNCTIONAL = FunctionalTesting(
                bases=(languagemovefolders,), name="languagemovefolders_FUNCTIONAL")
