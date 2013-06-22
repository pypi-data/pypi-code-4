"""
.. module:: base
   :synopsis: Base classes and containers.

.. moduleauthor:: Artur Barseghyan <artur.barseghyan@gmail.com>
"""
from dateutil.parser import parse

from django.core.paginator import Paginator, InvalidPage

from sirep.constants import GET_PARAM_DATE_LOWER, GET_PARAM_DATE_UPPER, GET_PARAM_PAGE, GET_PARAM_PER_PAGE
from sirep.conf import get_setting

REPORT_NUMBER_OF_ITEMS_PER_PAGE = get_setting('REPORT_NUMBER_OF_ITEMS_PER_PAGE')

SORT_VAR = 's'
SORTTYPE_VAR = 'st'

class Report(object):
    """
    The only thing a simple report would lack is sorting options. But we could implement something for that too.
    Everything is very simple. We define a base queryset, define a way to process the data and that's all.
    Redefine the ``process_data`` method in your class, define names of the fields and that's all. In most of the
    cases in your ``process_data`` you would be processing data from already processed queryset. Since the
    ``Report`` class is HttpRequest responsive (it knows the given request paramters), you would just
    need to use the ``get_queryset`` method to get the queryset (example: queryset = self.get_queryset()) and further
    do as shown in the example below.

    There are some obligatory attributes that should be set in the child class:
        ``verbose_name``
        ``fields``
        ``queryset``

    If you want to have the date filtering set, you should provide the following attribute as well:
        ``date_field``

    There's no ordering, since that's done on the queryset side.

    Example of ``fields`` value:
        >>> fields = [u'Article ID', u'Headline', u'Slug', u'URL', u'Author', u'Date published', u'Word Count']
    Example of ``process_data``:
        >>> def process_data(self):
        >>>     word_count = lambda s : len(s.split())
        >>>     get_word_count = lambda a : word_count(strip_tags('\r\n'.join([p.content for p in a.page_set_all])))
        >>>
        >>>     queryset = self.get_queryset()
        >>>
        >>>     self.items = []
        >>>     for a in queryset:
        >>>         self.items.append([
        >>>             a.pk,
        >>>             a.headline,
        >>>             a.slug,
        >>>             a.get_absolute_url(),
        >>>             a.author.username,
        >>>             a.date_published,
        >>>             get_word_count(a)
        >>>             ])

        NOTE: ``process_data`` has to update the ``self.items``, which is a list of lists. Each so called row in the
        list shall have same number of items as the ``self.fields``.
    """
    verbose_name = None
    items = []
    fields = []
    queryset = None
    date_field = None
    limit = REPORT_NUMBER_OF_ITEMS_PER_PAGE

    # Pagination data
    paginator = None
    page_obj = None
    results_per_page = None
    has_next = None
    has_previous = None
    page = None
    next = None
    previous = None
    first_on_page = None
    last_on_page = None
    pages = None
    hits = None
    page_range = None

    def __init__(self, request):
        if self.queryset is None:
            raise NotImplementedError("You should provide a ``queryset`` attribute in your class!")

        if self.fields in (None, [], ''):
            raise NotImplementedError("You should provide a ``fields`` attribute in your class!")

        if self.verbose_name in (None, ''):
            raise NotImplementedError("You should provide a ``verbose_name`` attribute in your class!")

        self.request = request
        self.params = dict(self.request.GET.items())

        self.sort_by = int(self.params.get(SORT_VAR, '0'))
        self.sort_type = self.params.get(SORTTYPE_VAR, 'asc')

        self.process_data()

    def get_headers(self):
        """
        Gets report headers (field titles).

        :return list:
        """
        return self.fields

    def get_date_lower(self):
        """
        Gets lower date range (from request).

        :return datetime.datetime:
        """
        d = self.request.GET.get(GET_PARAM_DATE_LOWER, None)
        if d:
            try:
                self.date_lower = parse(d)
            except Exception, e:
                self.date_lower = None
        else:
            self.date_lower = None
        return self.date_lower

    def get_date_upper(self):
        """
        Gets upper date range (from request).

        :return datetime.datetime:
        """
        d = self.request.GET.get(GET_PARAM_DATE_UPPER, None)
        if d:
            try:
                self.date_upper = parse(d)
            except Exception, e:
                self.date_upper = None
        else:
            self.date_upper = None
        return self.date_upper

    def get_limit(self):
        """
        Gets limit per page. Tries to use the GET parameter of the HttpRequest (even if it's empty). Otherwise relies
        on the ``limit`` value defined in the class (default value ``SIMPLE_REPORT_NUMBER_OF_ITEMS_PER_PAGE`` overridable in
        local settings).

        :return int:
        """
        if self.request.GET.has_key(GET_PARAM_PER_PAGE):
            try:
                return int(self.request.GET.get(GET_PARAM_PER_PAGE))
            except Exception, e:
                return None
        else:
            return self.limit

    def get_page(self):
        """
        Gets the page number (from request).

        :return int:
        """
        page = self.request.GET.get(GET_PARAM_PAGE, 1)
        if not page:
            page = 1
        return page

    def get_queryset(self):
        """
        Gets the queryset based on the request. Also, makes appropriate modifications to the pagination.

        :return django.db.models.query.QuerySet:
        """
        queryset = self.queryset

        # If lower date range specified, we update the queryset
        if self.get_date_lower() and self.date_field is not None:
            filter = {self.date_field + '__gte': self.get_date_lower()}
            queryset = queryset.filter(**filter)

        # If upper date range specified, we update the queryset
        if self.get_date_upper() and self.date_field is not None:
            filter = {self.date_field + '__lte': self.get_date_upper()}
            queryset = queryset.filter(**filter)

        # If limit is specified, we slice the queryset. NOTE: After this is done, we can't update the queryset
        # anymore, since it will be frozen.
        if self.get_limit() not in (None, '', 0, '0', 'all'):
            paginator = Paginator(queryset, self.get_limit(), allow_empty_first_page=False)
            page = self.get_page()
            try:
                page_number = int(page)
            except ValueError, e:
                if 'last' == page:
                    page_number = paginator.num_pages
                else:
                    raise Exception("Invalid page number")

            try:
                page_obj = paginator.page(page_number)
            except InvalidPage, e:
                raise Exception("Invalid page")

            # Paginated objects
            self.paginator = paginator
            self.page_obj = page_obj
            self.results_per_page = paginator.per_page
            self.has_next = page_obj.has_next()
            self.has_previous = page_obj.has_previous()
            self.page = page_obj.number
            self.next = page_obj.next_page_number() if (page_obj.has_next() and page_obj.next_page_number() is not None) else ''
            self.previous = page_obj.previous_page_number() if (page_obj.has_previous() and page_obj.previous_page_number() is not None) else ''
            self.first_on_page = page_obj.start_index()
            self.last_on_page = page_obj.end_index()
            self.pages = paginator.num_pages
            self.hits = paginator.count
            self.page_range = paginator.page_range
            return page_obj.object_list

        return queryset

    def process_data(self):
        """
        This method shall make a plain list of the ``self.queryset`` and save it back to the ``self.items``.
        """
        raise NotImplementedError("You should define a ``process_data`` method in your class and collect the data there!")

class ReportContainer(object):
    """
    Report container.
    """
    __slots__ = ('slug', 'report')

    def __init__(self, slug, report):
        """
        Construct the report container (easy to use in templates).

        :param str slug: Report slug.
        :param sirep.base.Report cls: Report class being registered.
        """
        self.slug = slug
        self.report = report

    def verbose_name(self):
        """
        Gets verbose name of the report.

        :return str:
        """
        return self.report.verbose_name
