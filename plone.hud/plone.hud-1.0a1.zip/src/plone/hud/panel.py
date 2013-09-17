# -*- coding: utf-8 -*-
"""HUD panel view to be extended by individual panels."""

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.hud import _
from plone.hud.misc import CONFIGLET_CATEGORY
from plone.memoize.view import memoize

import logging

logger = logging.getLogger("plone.app.hud.panel")


class HUDPanelView(BrowserView):
    main_template = ViewPageTemplateFile('browser/templates/panel.pt')

    def render(self):
        self.portal = api.portal.get()
        self.portal_url = self.portal.absolute_url() + "/"
        self.hud_title = _(u"HUD Panels")
        self.hud_url = "{0}@@hud".format(self.portal_url)
        panels = self.list_panels()
        if panels:
            self.first_panel = panels[0]
            if "panel_name" in self.request.form:
                name = self.request.form["panel_name"]
            else:
                name = self.first_panel["name"]
            self.current_panel = self.get_panel(name)
        else:
            self.first_panel = None
            self.current_panel = None
        return self.main_template()

    def __call__(self):
        return self.render()

    def panel_view(self):
        panel = self.portal.restrictedTraverse(self.current_panel["name"])
        return panel.render()

    def get_panels(self):
        portal_controlpanel = api.portal.get_tool(name='portal_controlpanel')
        configlets = portal_controlpanel.enumConfiglets(
            group=CONFIGLET_CATEGORY
        )
        result = []
        for configlet in configlets:
            name = configlet["url"].replace(self.portal_url, "")
            name = name.replace("@@", "")
            try:
                panel = self.portal.restrictedTraverse(name)
                if not panel:
                    continue
                title = getattr(panel, 'title', None)
                result += [{
                    "title": title if title else configlet["title"],
                    "name": name,
                    "url": "{0}@@hud?panel_name={1}".format(
                        self.portal_url, name
                    )
                }]
            except KeyError as ke:
                logger.warning("KeyError message: {0}".format(ke.message))
        return result

    def get_panel(self, name):
        for panel in self.list_panels():
            if panel["name"] == name:
                return panel
        return None

    @memoize
    def list_panels(self):
        return self.get_panels()
