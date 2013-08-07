# encoding: utf-8
"""
Custom managers for the Django weblog app.

"""
import datetime

from django.db import models


class PostManager(models.Manager):
    """Simplyfies getting published posts."""

    def get_query_set(self):
        """Return all posts marked as published."""
        return super(PostManager, self).get_query_set().filter(
                status__exact=self.model.STATUS_PUBLISHED).order_by(
                '-pub_date')

    def in_category(self, category):
        """Return all posts that are in a given category."""
        if not category:
            return self.filter(categories=None)
        return self.filter(
                categories__path__startswith=category.path)

    def by_date_and_slug(self, year, month, day, slug):
        """Get the post specified by the given date and slug."""
        date = datetime.date(year, month, day)
        date_range = (datetime.datetime.combine(date, datetime.time.min),
                datetime.datetime.combine(date, datetime.time.max))
        return self.get(pub_date__range=date_range,
                slug__exact=slug)


class PostCountManager(PostManager):
    """Get the number of posts per year, month, category or tag."""

    def by_year(self, year):
        """Post in a certain year, where ``year`` can be a string or an int."""
        return self.filter(pub_date__year=int(year)).count()

    def by_month(self, year, month=None):
        """
        Post in a certain month. You can either pass ``year`` and ``month``
        as separate ints or just ``year`` as string with the format 'YYYYMM'.

        """
        if isinstance(year, basestring) and not month:
            year, month = int(year[0:4]), int(year[4:6])
        else:
            year, month = int(year), int(month)

        return self.filter(pub_date__year=year,
                pub_date__month=month).count()

    def by_category(self, category):
        """Posts that are in a certain category."""
        return self.in_category(category).count()

    def by_tag(self, tag):
        """Posts tagged with a certain tag."""
        pass
