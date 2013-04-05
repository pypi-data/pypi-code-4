import math

from django.core.paginator import Paginator, Page


"""
Pagination classes for windowed/ranged pagination.
These classes build on the pagination built in to Django and add functionality
so you can paginate a la:

    1 ... 5, 6, 7, 8 ... 32

See https://docs.djangoproject.com/en/1.4/topics/pagination/ for general
usage--we simply add a `window` argument to the class constructors for
Paginator/Page on top of what they already support.

"""


class WindowedPaginator(Paginator):

    def page(self, number, window=None):

        """
        Returns a Page object for the given 1-based page number.
        This is a copy of Paginator.page, but returning a WindowedPage
        instance instead of a Page one
        """

        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        if top + self.orphans >= self.count:
            top = self.count
        return WindowedPage(self.object_list[bottom:top], number, self,
                            window=window)


class WindowedPage(Page):

    def __init__(self, object_list, number, paginator, window=None):

        """
        WindowedPage object constructor

        `window`    integer     A number indicating how many page links
                                you want to display in between the first and
                                last pages. Example: a value of '5' with a
                                total of 30 pages, on page 14 would yield a
                                page range of:
                                [1, None, 12, 13, 14, 15, 16, None, 30]
        """

        super(WindowedPage, self).__init__(object_list, number, paginator)
        self.window = window

    def _get_page_range(self):

        # If a window is set, and that window plus the first and last pages
        # is less than the total...

        if self.window and self.window + 2 < self.paginator.num_pages:

            # Calculate lower and higher window limits

            page_max = self.paginator.num_pages
            offset = int(math.floor(float(self.window - 1) / 2))
            lower = self.number - offset
            higher = self.number + (self.window - offset)

            if lower <= 2:
                lower = 2
                higher = 2 + self.window
            elif higher >= page_max:
                higher = page_max
                lower = higher - self.window

            # Build pages list

            pages = [1]

            if lower > 2:
                pages.append(None)

            pages.extend(range(lower, higher))

            if higher < page_max - 1:
                pages.append(None)

            pages.append(page_max)

            return pages
        else:
            return self.paginator._get_page_range()

    page_range = property(_get_page_range)
