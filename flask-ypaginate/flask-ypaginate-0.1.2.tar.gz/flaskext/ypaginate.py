#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import unicode_literals
from flask import request, url_for

class Pagination():
    '''A simple pagination extension for flask'''
    activePageHtml = '<li class="active"><a href="{0}">{1}</a></li>'
    linkHtml = '<li><a href="{0}">{1}</a></li>'
    prevLabel = ' &laquo; '
    nextLabel = ' &raquo; '
    prevPageHtml = '<li><a href="{0}">{1}</a></li>'
    nextPageHtml = '<li><a href="{0}">{1}</a></li>'
    first_pageHtml = '<li class="disabled"><a href="#">{0}</a></li>'
    last_pageHtml = '<li class="disabled"><a href="#">{0}</a></li>'
    disabledPageHtml = '<li class="disabled"><a href="#">{0}</a></li>'
    linkCss = '<div class="pagination{0}{1}"><ul>'
    recordName = 'records'
    displayMsg = '''Displaying <b>{start} - {end}</b> {recordName} in total
    <b>{total}</b>'''
    searchMsg = '''Found <b>{found}</b> {recordName} in total <b>{total}</b>,
    displaying <b>{start} - {end}</b>'''
    gapMarker = '<li class="disabled"><a href="#">...</a></li>'
    classicActivePageHtml = '<li class="active"><a href="#">{0}</a></li>'

    MODE_ORIGINAL = 1
    MODE_SIMPLE   = 2
    MODE_FIXED    = 3

    def __init__(self, found=0, **kwargs):
        '''provides the params:

            **mode**: One of:
                      Pagination.MODE_ORIGINAL - flask-paginate style
                                                 link generation.
                                                 This is the default value.
                      Pagination.MODE_SIMPLE   - simple url generation
                      Pagination.MODE_FIXED    - similar to flask-paginate
                                                 style link generation, but with
                                                 some bugs fixed.

            **endpoint**: url endpoint.

                          If self.mode is Pagination.MODE_ORIGINAL, this is
                          ignored, and self.endpoint is set to request.endpoint

                          If self.mode is Pagination.MODE_SIMPLE, the value
                          of endpoint should be a string and it is used for
                          URL generation.

                          If self.mode is Pagination.MODE_FIXED, endpoint should
                          be the name of the view function, which will be
                          passed to flask.url_for for link generation.

            **found**: used when searching

            **page**: current page

            **perPage**: how many links displayed on one page

            **pageSep**: Defaults to 'perPage'.

                         If self.mode is Pagination.MODE_SIMPLE, this is the
                         path preceding the integer page value in a generated
                         page url.

                         If self.mode is Pagination.MODE_FIXED, this is the
                         request.args variable name in the flask url endpoint
                         that will be substituted with an integer page value.

            **perPageSep**: Defaults to 'perPage'.

                            If self.mode is Pagination.MODE_SIMPLE, this is the
                            path preceding the integer perPage value in a
                            generated page url.

                            If self.mode is Pagination.MODE_FIXED, this is the
                            request.args variable name in the flask url endpoint
                            that will be substituted with an integer perPage
                            value. If no string is supplied, request.endpoint
                            is used.

            **innerWindow**: number of links before and after the current page.

                            If this is set to 2, then in Pagination.links,
                            2 pages will come before the current page, and
                            2 pages will come after the current page.

                            Suppose that there are 30 pages, our current page
                            is 10, and innerWindow is set to 3. Then the
                            "middle section" of Pagination.links will look
                            consist of pages 7, 8, 9, 10, 11, 12, 13.

                            The default value of innerWindow is 1

            **outerWindow**: number of links after the first page / before the last page.
                             Suppose that this is set to 2 and there are 20
                             pages in total. Then the left outerWindow will
                             consist of pages 1, 2, 3 and the right outerWindow
                             will consist of pages 18, 19, 20.

                             The default value of outerWindow is 2

            **prevLabel**: text for previous page, default is **&laquo;**

            **nextLabel**: text for next page, default is **&raquo;**

            **search**: search or not?

            **total**: total records for pagination

            **displayMsg**: text for pagination information

            **searchMsg**: text for search information

            **recordName**: record name showed in pagination information

            **linkSize**: font size of page links

            **alignment**: the alignment of pagination links
        '''
        self.found = found
        self.mode = kwargs.get('mode', Pagination.MODE_ORIGINAL)
        self.page = kwargs.get('page', 1)
        self.perPage = kwargs.get('perPage', 10)
        self.pageSep = kwargs.get('pageSep', 'page')
        self.perPageSep = kwargs.get('perPageSep', 'perPage')
        self.endpoint = kwargs.get('endpoint', None)
        if self.mode == Pagination.MODE_ORIGINAL:
            self.endpoint = request.endpoint
        if self.mode == Pagination.MODE_FIXED and self.endpoint is None:
            self.endpoint = request.endpoint
        self.innerWindow = kwargs.get('innerWindow', 2)
        self.outerWindow = kwargs.get('outerWindow', 1)
        self.prevLabel = kwargs.get('prevLabel') or Pagination.prevLabel
        self.nextLabel = kwargs.get('nextLabel') or Pagination.nextLabel
        self.search = kwargs.get('search', False)
        self.total = kwargs.get('total', 0)
        self.displayMsg = kwargs.get('displayMsg') or Pagination.displayMsg
        self.searchMsg = kwargs.get('searchMsg') or Pagination.searchMsg
        self.recordName = kwargs.get('recordName') or Pagination.recordName
        self.linkSize = kwargs.get('linkSize', '')
        if self.linkSize:
            self.linkSize = ' pagination-{0}'.format(self.linkSize)

        self.alignment = kwargs.get('alignment', 'centered')
        self.alignment = ' pagination-{0}'.format(self.alignment)

    @property
    def args(self):
        args = dict(request.args.to_dict().items() + request.view_args.items())
        if self.mode == Pagination.MODE_FIXED:
            # Fixed mode. Pop off the variable names for pageSep and perPageSep.
            # The <pageSep> portion of the url will be replaced by either:
            #   - a page argument to a Pagination method
            #   - self.page
            # during the link generation process
            #
            # The <perPageSep> portion of the url will be replaced by
            # self.perPage during the link generation process
            args.pop(self.pageSep, None)
            args.pop(self.perPageSep, None)
        else:
            args.pop('page', None)
        return args

    @property
    def total_pages(self):
        pages = divmod(self.total, self.perPage)
        return pages[0] + 1 if pages[1] else pages[0]

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.total_pages

    @property
    def prev_page(self):
        if self.mode == Pagination.MODE_ORIGINAL:
            if self.has_prev:
                page = self.page - 1 if self.page > 2 else None
                return Pagination.prevPageHtml.format(url_for(self.endpoint,
                                                              page=page,
                                                              **self.args
                                                             ),
                                                      self.prevLabel
                                                     )
            else:
                return Pagination.disabledPageHtml.format(self.prevLabel)
        elif self.mode == Pagination.MODE_FIXED:
            if self.has_prev:
                argsDict = {
                    self.pageSep: self.page - 1,
                    self.perPageSep: self.perPage,
                }
                argsDict.update(self.args)
                return Pagination.prevPageHtml.format(url_for(self.endpoint,
                                                              **argsDict),
                                                      self.prevLabel)
            else:
                return Pagination.disabledPageHtml.format(self.prevLabel)
        else:
            if self.has_prev:
                return Pagination.prevPageHtml.format(self.pageUrl(self.page - 1),
                    self.prevLabel)
            else:
                return Pagination.disabledPageHtml.format(self.prevLabel)

    @property
    def next_page(self):
        if self.mode == Pagination.MODE_ORIGINAL:
            if self.has_next:
                return Pagination.nextPageHtml.format(url_for(self.endpoint,
                                                              page=self.page + 1,
                                                              **self.args
                                                             ),
                                                      self.nextLabel
                                                     )
            else:
                return Pagination.disabledPageHtml.format(self.nextLabel)
        elif self.mode == Pagination.MODE_FIXED:
            if self.has_next:
                argsDict = {
                    self.pageSep: self.page + 1,
                    self.perPageSep: self.perPage,
                }
                argsDict.update(self.args)
                return Pagination.nextPageHtml.format(url_for(self.endpoint,
                                                              **argsDict),
                                                      self.nextLabel
                                                     )
            else:
                return Pagination.disabledPageHtml.format(self.nextLabel)
        else:
            if self.has_next:
                return Pagination.nextPageHtml.format(self.pageUrl(self.page + 1),
                    self.nextLabel)
            else:
                return Pagination.disabledPageHtml.format(self.nextLabel)

    @property
    def first_page(self):
        if self.mode == Pagination.MODE_ORIGINAL:
            if self.has_prev:
                return Pagination.linkHtml.format(
                        url_for(self.endpoint, **self.args), 1)
            else:
                return Pagination.classicActivePageHtml.format(1)
        elif self.mode == Pagination.MODE_FIXED:
            if self.has_prev:
                argsDict = {
                    self.pageSep: 1,
                    self.perPageSep: self.perPage,
                }
                argsDict.update(self.args)
                return Pagination.linkHtml.format(
                        url_for(self.endpoint, **argsDict), 1)
            else:
                return Pagination.classicActivePageHtml.format(1)
        else:
            if self.has_prev:
                return Pagination.linkHtml.format(self.pageUrl(1), 1)
            else:
                # current page is first page
                return self.active_page(1)

    @property
    def last_page(self):
        if self.mode == Pagination.MODE_ORIGINAL:
            if self.has_next:
                return Pagination.linkHtml.format(
                        url_for(self.endpoint, page=self.total_pages,
                            **self.args),
                        self.total_pages)
            else:
                return Pagination.classicActivePageHtml.format(self.page)
        elif self.mode == Pagination.MODE_FIXED:
            if self.has_next:
                argsDict = {
                    self.pageSep: self.total_pages,
                    self.perPageSep: self.perPage,
                }
                argsDict.update(self.args)
                return Pagination.linkHtml.format(
                        url_for(self.endpoint, **argsDict),
                        self.total_pages)
            else:
                return Pagination.classicActivePageHtml.format(self.total_pages)
        else:
            if self.has_next:
                return Pagination.linkHtml.format(self.pageUrl(self.total_pages),
                    self.total_pages)
            else:
                return self.active_page(self.total_pages)

    def active_page(self, page):
        '''
        returns the html for an active page
        '''
        return Pagination.activePageHtml.format(self.pageSep, page,
            self.perPageSep, self.perPage, page)

    def pageUrl(self, page):
        return self.endpoint + ('/' if self.endpoint[-1] != '/' else '') + \
            self.pageSep + '/' + str(page) + '/' + \
            self.perPageSep + '/' + str(self.perPage)

    def single_page(self, page):
        if self.mode == Pagination.MODE_ORIGINAL:
            if page <= 0:
                return self.first_page

            if page > self.total_pages:
                return self.last_page

            if page == self.page:
                return Pagination.classicActivePageHtml.format(page)

            if page == 1:
                return self.first_page

            if page == self.total_pages:
                return self.last_page

            return Pagination.linkHtml.format(url_for(self.endpoint, page=page,
                    **self.args), page)

        elif self.mode == Pagination.MODE_FIXED:
            if page <= 0:
                return self.first_page

            if page > self.total_pages:
                return self.last_page

            if page == self.page:
                return Pagination.classicActivePageHtml.format(page)

            if page == 1:
                return self.first_page

            if page == self.total_pages:
                return self.last_page

            argsDict = {
                self.pageSep: page,
                self.perPageSep: self.perPage,
            }
            argsDict.update(self.args)
            return Pagination.linkHtml.format(
                    url_for(self.endpoint, **argsDict), page)
        else:
            if page <= 0:
                return self.first_page

            if page > self.total_pages:
                return self.last_page

            if page == self.page:
                return self.active_page(page)

            if page == 1:
                return self.first_page

            if page == self.total_pages:
                return self.last_page

            return Pagination.linkHtml.format(self.pageUrl(page), page)

    @property
    def pages(self):
        '''
        Produces a list of pages

        Ultimately, this should look like:

        <- firstPage ow ->   <- iw currentPage iw ->  <- ow lastPage ->

        where ow is outerWindow, and iw is innerWindow
        '''
        if self.total_pages <= self.innerWindow * 2 + 1:
            # if 2 innerWindows and current page already takes up the entire range
            # of pages, we can just return a list from 1...total_pages
            return list(xrange(1, self.total_pages + 1))

        pages = []
        # create the middle portion (iw currentPage iw)
        winFrom = self.page - self.innerWindow
        winTo = self.page + self.innerWindow
        if winTo > self.total_pages:
            # end of middle section exceeds totalPages, we slide pages to
            # the left by difference between winTo and total_pages
            winFrom -= winTo - self.total_pages
            winTo = self.total_pages
        # This "if winFrom < 1" section seems to be unnecessary
        # Reason being, self.total_pages > self.innerWindow * 2 + 1 , and
        # winTo - winFrom + 1 is precisely self.innerWindow * 2 + 1
        # So even if winTo > self.total_pages, shifting winFrom back by
        #     winTo - self.total_pages should not cause winFrom to be < 1,
        # otherwise this will violate self.total_pages > self.innerWindow * 2 + 1

        #if winFrom < 1:
        #    # possibly after sliding, start of middle section (winFrom) falls
        #    # outside of page range. slide pages back to the right such that
        #    # winFrom becomes 1
        #    winTo = winTo + 1 - winFrom
        #    winFrom = 1
        #    if winTo > self.total_pages:
        #        # now, end of middle section (winTo) goes past page range.
        #        # set end of middle section to total_pages
        #        winTo = self.total_pages
        middleSectionAppended = False
        if winFrom > self.outerWindow + 1 + 1:
            # left section neither touches nor overlaps with middle section.
            # Append entire [1..outerWindow]
            pages.extend(list(xrange(1, self.outerWindow + 1 + 1)))
        else:
            # left section touches/overlaps with middle section
            # Just append [1..winTo] to pages
            pages.extend(list(xrange(1, winTo + 1)))
            middleSectionAppended = True

        # What's remaining is to determine whether the right section
        # touches / overlaps with the middle section
        if winTo < self.total_pages - self.outerWindow - 1:
            # end of middle section does not touch/overlap right section
            if not middleSectionAppended:
                # middle section not appended, append separator, then append it
                pages.append(None)
                pages.extend(list(xrange(winFrom, winTo+1)))
            # append separator, followed by right section
            pages.append(None)
            pages.extend(list(xrange(self.total_pages - self.outerWindow,
                self.total_pages + 1)))
        else:
            # middle section touches/overlaps with right section
            if not middleSectionAppended:
                # middle section not appended. Append separator, then append
                # start of middle section all the way to the end of everything
                pages.append(None)
                pages.extend(list(xrange(winFrom, self.total_pages + 1)))
            else:
                # middle section has been appended
                # append from 1 past middle section to the end of everything
                pages.extend(list(xrange(winTo + 1, self.total_pages + 1)))
        return pages

    @property
    def links(self):
        '''get all the pagination links'''
        if self.total_pages <= 1:
            return ''

        s = [Pagination.linkCss.format(self.linkSize, self.alignment)]
        s.append(self.prev_page)
        for page in self.pages:
            s.append(self.single_page(page) if page else Pagination.gapMarker)

        s.append(self.next_page)
        s.append('</ul></div>')
        return ''.join(s)

    @property
    def info(self):
        '''get the pagination information'''
        start = 1 + (self.page - 1) * self.perPage
        end = start + self.perPage - 1
        if end > self.total:
            end = self.total if not self.search else self.found

        if start > self.total:
            start = self.total if not self.search else self.found

        s = ['<div class="pagination-page-info">']
        page_msg = self.searchMsg if self.search else self.displayMsg
        s.append(page_msg.format(found=self.found,
                                 total=self.total,
                                 start=start,
                                 end=end,
                                 recordName=self.recordName,
                                 )
                 )
        s.append('</div>')
        return ''.join(s)
