# -*- coding: utf-8 -*-

from ralph.routers import BaseRouter


class RalphAssetsRouter(BaseRouter):
    db_name = 'ralph_assets'
    app_name = 'ralph_assets'


class RalphDiscoveryRouter(BaseRouter):
    db_name = 'ralph'
    app_name = 'discovery'
