from plone.directives import form
from seantis.people.types.base import PersonBase


class IPHZ(form.Schema):
    form.model("phz.xml")


class PHZ(PersonBase):

    @property
    def org_units(self):
        return [org for org in (self.org_unit_1, self.org_unit_2) if org]
