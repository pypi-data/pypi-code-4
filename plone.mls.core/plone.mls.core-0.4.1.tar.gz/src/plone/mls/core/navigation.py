# -*- coding: utf-8 -*-
"""Custom Batch Provider for listing results."""

# zope imports
from Products.CMFPlone.PloneBatch import Batch


class ListingBatch(Batch):
    """Listing result batch."""

    def __init__(self, sequence, size, start=0, end=0, orphan=0, overlap=0,
                 pagerange=7, quantumleap=0, b_start_str='b_start',
                 batch_data=None):
        self.batch_data = batch_data

        if sequence is None:
            sequence = []

        super(ListingBatch, self).__init__(
            sequence, size, start, end, orphan, overlap, pagerange,
            quantumleap, b_start_str,
        )

    @property
    def sequence_length(self):
        """Effective length of sequence."""
        if self.batch_data is not None:
            length = getattr(self, 'pagesize', 0)
            return self.batch_data.get('results', length)
        return super(ListingBatch, self).sequence_length

    def __getitem__(self, index):
        if index >= self.length:
            raise IndexError(index)
        return self._sequence[index]

    @property
    def next(self):
        """Next batch page."""
        if self.end >= (self.last + self.pagesize):
            return None
        return ListingBatch(
            self._sequence, self._size, self.end - self.overlap, 0,
            self.orphan, self.overlap, batch_data=self.batch_data,
        )

    @property
    def previous(self):
        """Previous batch page."""
        if not self.first:
            return None
        return ListingBatch(
            self._sequence, self._size, self.first - self._size + self.overlap,
            0, self.orphan, self.overlap, batch_data=self.batch_data,
        )
