import datetime
from django.db.models import Sum
from django.db.models.query import EmptyQuerySet, QuerySet
from kiowa.utils import get_attr


registry = {}


class FakeQuerySet(EmptyQuerySet):
    """Turn a list into a Django QuerySet... kind of."""
    def __init__(self, model=None, query=None, using=None, items=[]):
        super(FakeQuerySet, self).__init__(model, query, using)
        self._result_cache = items

    def count(self):
        return len(self)


class SubTotalGroup(list):

    def __getattr__(self, fieldname):
        tot = 0
        for el in self:
            attr = get_attr(el, fieldname)
            if callable(attr):
                tot += attr()
            else:
                tot += attr or 0
        return tot


class SubTotalList(object):
    def __init__(self, *groups):
        self.groups = groups
        self._entries = {}

    def __getitem__(self, y):
        if not y in self._entries:
            self._entries[y] = SubTotalGroup()
        return self._entries[y]

    def get_unique_key_for_target(self, target):
        return "_".join([str(get_attr(target, g)) for g in self.groups])

    def process(self, target):
        hash = self.get_unique_key_for_target(target)
        self[hash].append(target)
        return self[hash]

    def __repr__(self):
        return "<Subtotal on %s >" % repr(self.groups)


class PostProcessor(QuerySet):
    allow_filtering = True
    allow_grouping = True
    allow_grouping = True

    def __init__(self, model=None, query=None, using=None, report=None, queryset=None):
        self._report = report
        self._queryset = queryset
        super(PostProcessor, self).__init__(model, query, using)

    def _clone(self, klass=None, setup=False, **kwargs):
        if klass is None:
            klass = self.__class__
        query = self.query.clone()
        if self._sticky_filter:
            query.filter_is_sticky = True
        c = klass(model=self.model, query=query, using=self._db, report=self._report, queryset=self._queryset)
        c._for_write = self._for_write
        c._prefetch_related_lookups = self._prefetch_related_lookups[:]
        c.__dict__.update(kwargs)
        if setup and hasattr(c, '_setup_query'):
            c._setup_query()
        return c


class SubTotalPostProcessor(PostProcessor):
    def all(self):
        processed = {}
        x = self._clone()
        if self._report.groupby:
            total = SubTotalList(*self._report.get_target_grouping())
            for el in x:
                unique_key = total.get_unique_key_for_target(el)
                el.subtotal_group = total.process(el)
                processed[unique_key] = el.pk

        return filter(lambda x: x.id not in processed.values(), x)


class ContractPostProcessor(PostProcessor):

    def filter(self, *args, **kwargs):
        return self._clone()

    def active(self, *args, **kwargs):
        return self._clone()

    def inactive(self, *args, **kwargs):
        from pasportng.pasport.models import Contract
        return Contract.objects.latest_contracts(*args, **kwargs)


class LeavePostProcessor(PostProcessor):
    def all(self):
        _all = self._clone()
        for contract in _all:
            deadline = datetime.date.today() if not contract.expired else contract.nte
            contract.accruer_annual_leaves = contract.accruer.annual_leaves(deadline)
            contract.accruer_annual_leaves_taken = contract.accruer.annual_leaves_taken(deadline)
            contract.accruer_annual_leaves_balance = contract.accruer.annual_leaves_balance(deadline)

            contract.accruer_sick_leaves = contract.accruer.sick_leaves(deadline)
            contract.accruer_sick_leaves_balance = contract.accruer.sick_leaves_balance(deadline)

            contract.accruer_cto_leaves_taken = contract.accruer.cto_leaves_taken(deadline)
            contract.accruer_cto_leaves_balance = contract.accruer.cto_leaves_balance(deadline)
            contract.accruer_paternity_maternity_leaves_taken = contract.accruer.paternity_maternity_leaves_taken(deadline)
        return _all


class SalaryAdvancePostProcessor(PostProcessor):

    def all(self):
        deadline = datetime.datetime.today()
        _all = self._clone().filter(withhold_payroll=False, nte__gte=deadline)
        toremove = []
        for contract in _all:
            contract.advance_initial_amount = - contract.advancebalance_set.latest_advance_or_zero()
            if contract.advance_initial_amount:
                # FIXME horrible I kwnow. Probably it's time to cleanup things inside the manager
                try:
                    last_advance = contract.advancebalance_set.advances().latest('date')
                    filters = {'date__gt': last_advance.date}
                except contract.DoesNotExist:
                    filters = {}

                contract.advanced_payback_so_far = contract.advancebalance_set.filter(**filters).aggregate(Sum('amount'))['amount__sum'] or 0
                contract.advance_remaning_amount = contract.advancebalance_set.balance()
                contract.advance_balance_after_payroll = max(contract.advance_remaning_amount - contract.advance_next_return_amount, 0)
            else:
                toremove.append(contract.pk)

        return filter(lambda x: x.id not in toremove, _all)


class SalaryOutsideBandPostProcessor(PostProcessor):

    def all(self):
        return(salary for salary in self._clone() if salary.is_outside_band)


registry['PostProcessor'] = PostProcessor
registry['SubTotalPostProcessor'] = SubTotalPostProcessor
registry['ContractPostProcessor'] = ContractPostProcessor
registry['SalaryAdvancePostProcessor'] = SalaryAdvancePostProcessor
registry['LeavePostProcessor'] = LeavePostProcessor
registry['SalaryOutsideBandPostProcessor'] = SalaryOutsideBandPostProcessor


