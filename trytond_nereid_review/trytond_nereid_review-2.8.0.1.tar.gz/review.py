# -*- coding: utf-8 -*-
"""
    review

    Nereid Reviews

    :copyright: (c) 2012-2013 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.model import ModelSQL, ModelView, fields

__all__ = ['NereidReview']


class NereidReview(ModelSQL, ModelView):
    "Nereid Review"
    __name__ = "nereid.review"
    _rec_name = 'title'

    title = fields.Char('Title')
    rating = fields.Integer('Rating (On a scale of 1-5)')
    comment = fields.Text('Comment')

    # Who wrote the review
    nereid_user = fields.Many2One(
        'nereid.user', 'Nereid User', required=True
    )
    party = fields.Function(
        fields.Many2One('party.party', 'Party'), 'get_party'
    )

    @classmethod
    def __setup__(cls):
        super(NereidReview, cls).__setup__()
        cls._sql_constraints += [(
            'valid_rating',
            'CHECK (rating BETWEEN 0 AND 5)',
            'invalid_rating',
        )]
        cls._error_messages = {
            'invalid_rating': 'The rating has to be on a scale of 1 to 5'
        }

    def get_party(self, name):
        """
        Get the party from the nereid user
        """
        return self.nereid_user and self.nereid_user.party.id or None
