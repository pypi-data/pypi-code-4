# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

# Python 2 and 3 compatibility utilities
import six

from blist import sorteddict

from .compress import compress_amount
from .mixins import SerializableMixin
from .serialize import serialize_leint, serialize_varint

from .script import ScriptPickler
_pickler = ScriptPickler()

class UnspentTransaction(SerializableMixin, sorteddict):
    def __init__(self, *args, **kwargs):
        if 'transaction' in kwargs and any(x in kwargs for x in
                ('coinbase', 'version', 'height', 'reference_height')):
            raise TypeError(u"instantiate by either specifying the "
                u"transaction directly or its individual meta-values, "
                u"but not both")
        transaction = kwargs.pop('transaction', None)

        version = kwargs.pop('version', 1)
        if version not in (2,) and 'reference_height' in kwargs:
            raise TypeError((u"reference_height must be implicit for "
                u"transaction version=%d") % version)

        is_coinbase = kwargs.pop('coinbase', False)
        height = kwargs.pop('height', 0)
        reference_height = kwargs.pop('reference_height', 0)

        super(UnspentTransaction, self).__init__(*args, **kwargs)

        if transaction is not None:
            self.version          = transaction.version
            self.is_coinbase      = transaction.is_coinbase
            self.height           = transaction.height
            self.reference_height = transaction.reference_height
            if not self:
                for idx,output in enumerate(transaction.outputs):
                    self[idx] = output
        else:
            self.version          = version
            self.is_coinbase      = is_coinbase
            self.height           = height
            self.reference_height = reference_height

    def serialize(self):
        code, bitvector = 0, 0
        for idx in six.iterkeys(self):
            bitvector |= 1 << idx
        if not bitvector:
            raise TypeError()
        code |= bitvector & 0x03
        bitvector >>= 2
        bitvector = serialize_leint(bitvector)
        bitvector_len = len(bitvector)
        if not code:
            bitvector_len -= 1
        code |= len(bitvector) << 2
        code <<= 1
        if self.is_coinbase:
            code |= 1

        result  = serialize_varint(self.version)
        result += serialize_varint(code)
        result += bitvector
        for output in six.itervalues(self):
            result += serialize_varint(compress_amount(output.amount))
            result += _pickler.dumps(output.contract)
        result += serialize_varint(self.height)
        if self.version in (2,):
            result += serialize_varint(self.reference_height)
        return result
    @classmethod
    def deserialize(cls, file_):
        return cls()

    def __eq__(self, other):
        if any((self.version     != other.version,
                self.is_coinbase != other.is_coinbase,
                self.height      != other.height)):
            return False
        if self.version in (2,) and self.reference_height != other.reference_height:
            return False
        return super(UnspentTransaction, self) == other
    __ne__ = lambda a,b:not a==b
    def __repr__(self):
        return '%s%s' % (
            self.__class__.__name__,
            super(UnspentTransaction, self).__repr__()[10:])

#
# End of File
#
