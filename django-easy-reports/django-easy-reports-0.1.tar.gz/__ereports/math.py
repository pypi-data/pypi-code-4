from django.utils.encoding import smart_unicode
from kiowa.utils import get_attr


class Column(list):
    pass


class PayslipGroup(list):

    def sum(self, fieldname):
        tot = 0
        for el in self:
            tot += (get_attr(el, fieldname) or 0)
        return tot


class Regrouper(dict):
    def get(self, k, d=None):
        if not k in self:
            self[k] = PayslipGroup()
        return super(Regrouper, self).get(k, d)

    def __getitem__(self, y):
        if not y in self:
            self[y] = PayslipGroup()
        return super(Regrouper, self).__getitem__(y)

    def values(self):
        return super(Regrouper, self).values()

    def keys(self):
        return super(Regrouper, self).keys()
    groups = keys

    def items(self):
        for k, v in dict.items(self):
            v.sort(key=lambda x: x.contract.employee.index_no)

        sorted = zip(self.keys(), self.values())
        sorted.sort(key=lambda x: smart_unicode(x[0]))
        abs_order = 1
        for group, ps in sorted:
            for payslip in ps:
                payslip.abs_order = abs_order
                abs_order += 1

        return sorted


class Totalizer(dict):
    def __init__(self):
        self.columns = {}

    def get(self, k, d=None):
        if not k in self:
            self[k] = Column()
        return super(Totalizer, self).get(k, d)

    def __getitem__(self, y):
        if not y in self:
            self[y] = Column()
        return super(Totalizer, self).__getitem__(y)
