from plone.dexterity.content import Container
from plone.directives import form


class IPHZ(form.Schema):
    form.model("phz.xml")


class PHZ(Container):

    @property
    def org_units(self):
        return [org for org in (self.org_unit_1, self.org_unit_2) if org]
