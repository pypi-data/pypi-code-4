# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Definitions of AMP commands for Amptrac.
"""

from twisted.protocols import amp

class FetchTicket(amp.Command):
    """
    Requests ticket info from data store.

    @param id: The ticket ID to look up

    @param asHTML: Whether to render comments/description as HTML or
    not. Will use Trac wiki formatting if available.

    Returns all ticket fields, including a list of comments/changes.
    """
    arguments = [('id', amp.Integer()),
                 ('asHTML', amp.Boolean(optional=True))]
    response = [('id', amp.Integer()),
                ('type', amp.Unicode()),
                ('time', amp.Integer()),
                ('changetime', amp.Integer()),
                ('component', amp.Unicode()),
                ('priority', amp.Unicode()),
                ('owner', amp.Unicode()),
                ('reporter', amp.Unicode()),
                ('cc', amp.Unicode()),
                ('status', amp.Unicode()),
                ('resolution', amp.Unicode()),
                ('summary', amp.Unicode()),
                ('description', amp.Unicode()),
                ('raw_description', amp.Unicode()),
                ('keywords', amp.Unicode()),
                ('branch', amp.Unicode()),
                ('branch_author', amp.Unicode()),
                ('launchpad_bug', amp.Unicode()),
                ('attachments', amp.AmpList([('filename', amp.Unicode()),
                                             ('size', amp.Integer()),
                                             ('time', amp.Integer()),
                                             ('description', amp.Unicode()),
                                             ('author', amp.Unicode()),
                                             ])),
                ('changes', amp.AmpList([('time', amp.Integer()),
                                         ('author', amp.Unicode()),
                                         ('field', amp.Unicode()),
                                         ('oldvalue', amp.Unicode()),
                                         ('newvalue', amp.Unicode())]))]



class FetchReviewTickets(amp.Command):
    """
    Requests list of review tickets from data store.

    Returns all ticket fields.
    """
    arguments = []
    response = [('tickets', amp.AmpList([('id', amp.Integer()),
                                         ('type', amp.Unicode()),
                                         ('time', amp.Integer()),
                                         ('changetime', amp.Integer()),
                                         ('component', amp.Unicode()),
                                         ('priority', amp.Unicode()),
                                         ('owner', amp.Unicode()),
                                         ('reporter', amp.Unicode()),
                                         ('cc', amp.Unicode()),
                                         ('status', amp.Unicode()),
                                         ('resolution', amp.Unicode()),
                                         ('summary', amp.Unicode()),
                                         ('keywords', amp.Unicode()),
                                         ('branch', amp.Unicode()),
                                         ('branch_author', amp.Unicode()),
                                         ('launchpad_bug', amp.Unicode())]))]




class UpdateTicket(amp.Command):
    """
    Updates a ticket in the data store with new values for fields.
    """
    arguments = [('id', amp.Integer()),
                 ('key', amp.Unicode()),
                 ('type', amp.Unicode(optional=True)),
                 ('component', amp.Unicode(optional=True)),
                 ('priority', amp.Unicode(optional=True)),
                 ('owner', amp.Unicode(optional=True)),
                 ('reporter', amp.Unicode(optional=True)),
                 ('cc', amp.Unicode(optional=True)),
                 ('status', amp.Unicode(optional=True)),
                 ('resolution', amp.Unicode(optional=True)),
                 ('summary', amp.Unicode(optional=True)),
                 ('description', amp.Unicode(optional=True)),
                 ('keywords', amp.Unicode(optional=True)),
                 ('branch', amp.Unicode(optional=True)),
                 ('branch_author', amp.Unicode(optional=True)),
                 ('launchpad_bug', amp.Unicode(optional=True)),
                 ('comment', amp.Unicode(optional=True))]
