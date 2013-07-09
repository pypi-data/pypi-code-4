# -*- coding: utf-8 -*-
"""
A template for unsigned transactions.

The MIT License (MIT)

Copyright (c) 2013 by Richard Kiss

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import io

from ..ecdsa import generator_secp256k1, public_pair_for_secret_exponent
from ..encoding import bitcoin_address_to_hash160_sec, double_sha256, from_bytes_32, public_pair_to_hash160_sec
from ..serialize import b2h, b2h_rev
from ..serialize.bitcoin_streamer import stream_struct

from .Tx import Tx
from .TxIn import TxIn
from .TxOut import TxOut

from .script import opcodes
from .script import tools
from .script.signing import solver
from .script.vm import verify_script

class ValidationFailureError(Exception): pass

SIGHASH_ALL = 1
SIGHASH_NONE = 2
SIGHASH_SINGLE = 3
SIGHASH_ANYONECANPAY = 0x80

from .UnsignedTxOut import UnsignedTxOut

class UnsignedTx(object):
    def __init__(self, version, unsigned_txs_out, new_txs_out, lock_timestamp=0):
        self.version = version
        self.unsigned_txs_out = list([c.clone() for c in unsigned_txs_out])
        self.new_txs_out = list(new_txs_out)
        self.lock_timestamp = lock_timestamp

    @classmethod
    def standard_tx(class_, previous_hash_index_txout_tuple_list, coin_value__bitcoin_address__tuple_list):
        """Create a standard transaction.
        previous_hash_index_txout_tuple_list: a list of pairs of the form (previous
          hash, previous index) corresponding to the source coins. You must
          have private keys for these incoming transactions.
        coin_value__bitcoin_address__tuple_list: a list of pairs of the
          form (satoshi_count, bitcoin_address) corresponding to the payees.
          The satoshi_count is an integer indicating number of Satoshis (there
          are 1e8 Satoshis in a Bitcoin) and bitcoin_address is a standard
          Bitcoin address like 1FKYxGDywd7giFbnmKdvYmVgBHB9B2HXMw.
        """

        new_txs_out = []
        STANDARD_SCRIPT_OUT = "OP_DUP OP_HASH160 %s OP_EQUALVERIFY OP_CHECKSIG"
        for coin_value, bitcoin_address in coin_value__bitcoin_address__tuple_list:
            hash160 = bitcoin_address_to_hash160_sec(bitcoin_address)
            script_text = STANDARD_SCRIPT_OUT % b2h(hash160)
            script_bin = tools.compile(script_text)
            new_txs_out.append(TxOut(coin_value, script_bin))

        unsigned_txs_out = [UnsignedTxOut(h, idx, tx_out.coin_value, tx_out.script) for h, idx, tx_out in previous_hash_index_txout_tuple_list]

        # TODO: what is this?
        version, lock_timestamp = 1, 0
        return class_(version, unsigned_txs_out, new_txs_out, lock_timestamp)

    @classmethod
    def from_tx(class_, tx, tx_out_for_hash_index_f):
        """Create an UnsignedTx given a Tx and a tx_out_db.
        tx: the Tx to use as a template
        tx_out_for_hash_index_f: function taking (hash, idx) and returning
            corresponding tx_out. Must be fully populated for the relevant
            transactions."""

        unsigned_txs_out = []
        for tx_in in tx.txs_in:
            tx_out = tx_out_for_hash_index_f(tx_in.previous_hash, tx_in.previous_index)
            if tx_out is None:
                raise ValidationFailureError("can't find source tx_out for %s" % tx_in)
            unsigned_txs_out.append(UnsignedTxOut(tx_in.previous_hash, tx_in.previous_index, tx_out.coin_value, tx_out.script))

        # TODO: what is this?
        version, lock_timestamp = 1, 0
        return class_(version, unsigned_txs_out, tx.txs_out, lock_timestamp)

    def partial_hash(self, unsigned_txs_out_idx, signature_type):
        """Return the canonical hash for a transaction. We need to
        remove references to the signature, since it's a signature
        of the hash before the signature is applied.

        tx_out_script: the script the coins for tx_in_idx are coming from
        tx_in_idx: where to put the tx_out_script
        signature_type: always seems to be SIGHASH_ALL
        """

        # first off, make a copy
        tx_tmp = UnsignedTx(self.version, self.unsigned_txs_out, self.new_txs_out, self.lock_timestamp)

        # In case concatenating two scripts ends up with two codeseparators,
        # or an extra one at the end, this prevents all those possible incompatibilities.
        tx_out_script = self.unsigned_txs_out[unsigned_txs_out_idx].script
        tx_out_script = tools.delete_subscript(tx_out_script, [opcodes.OP_CODESEPARATOR])

        # blank out other inputs' signatures
        for unsigned_tx_out in tx_tmp.unsigned_txs_out:
            unsigned_tx_out.script = b''
        tx_tmp.unsigned_txs_out[unsigned_txs_out_idx].script = tx_out_script

        # Blank out some of the outputs
        if (signature_type & 0x1f) == SIGHASH_NONE:
            # Wildcard payee
            tx_tmp.new_txs_out = []

            # Let the others update at will
            for i in range(len(tx_tmp.unsigned_txs_out)):
                if i != unsigned_txs_out_idx:
                    tx_tmp.unsigned_txs_out[i].sequence = 0

        elif (signature_type & 0x1f) == SIGHASH_SINGLE:
            # Only lockin the txout payee at same index as txin
            n_out = unsigned_txs_out_idx
            for i in range(n_out):
                # BRAIN DAMAGE: this is not cloned, so it may change other items
                tx_tmp.new_txs_out[i].coin_value = -1
                tx_tmp.new_txs_out[i].script = ''

            # Let the others update at will
            for i in range(len(tx_tmp.txs_in)):
                if i != unsigned_txs_out_idx:
                    tx_tmp.unsigned_txs_out[i].sequence = 0

        # Blank out other inputs completely, not recommended for open transactions
        if signature_type & SIGHASH_ANYONECANPAY:
            tx_tmp.unsigned_txs_out = [tx_tmp.unsigned_txs_out[unsigned_txs_out_idx]]

        s = io.BytesIO()
        stream_struct("LI", s, self.version, len(self.unsigned_txs_out))
        for t in self.unsigned_txs_out:
            t.stream(s)
        stream_struct("I", s, len(self.new_txs_out))
        for t in self.new_txs_out:
            t.stream(s)
        stream_struct("L", s, self.lock_timestamp)
        stream_struct("L", s, signature_type)
        return from_bytes_32(double_sha256(s.getvalue()))

    def sign(self, secret_exponents, public_pair_compressed_for_hash160_lookup=None):
        """Sign a standard transaction.
        secret_exponents:
            either an array of the relevant secret exponents OR
            a dictionary-like object that returns a secret_exponent for a public_pair.
            Do something like this:
               sefppl = dict(((public_pair_for_secret_exponent(generator_secp256k1, secret_exponent)) :
                   secret_exponent) for secret_exponent in secret_exponent_list)
        public_pair_compressed_for_hash160_lookup:
            an optional dictionary-like object that returns a tuple (public_pair, compressed) for the
            key public_pair_to_hash160_sec(public_pair, compressed=compressed)
            If this parameter is not included, it is generated by the list of secret exponents. However,
            if this list is long, it may take a long time.
        """

        # if secret_exponents is a list, we generate the lookup
        # build secret_exponent_for_public_pair_lookup

        if hasattr(secret_exponents, "get"):
            secret_exponent_for_public_pair_lookup = secret_exponents
        else:
            secret_exponent_for_public_pair_lookup = {}
            public_pair_compressed_for_hash160_lookup = {}
            for secret_exponent in secret_exponents:
                public_pair = public_pair_for_secret_exponent(generator_secp256k1, secret_exponent)
                secret_exponent_for_public_pair_lookup[public_pair] = secret_exponent
                public_pair_compressed_for_hash160_lookup[public_pair_to_hash160_sec(public_pair, compressed=True)] = (public_pair, True)
                public_pair_compressed_for_hash160_lookup[public_pair_to_hash160_sec(public_pair, compressed=False)] = (public_pair, False)

        new_txs_in = []
        for unsigned_tx_out_idx, unsigned_tx_out in enumerate(self.unsigned_txs_out):
            # Leave out the signature from the hash, since a signature can't sign itself.
            # The checksig op will also drop the signatures from its hash.
            partial_hash = self.partial_hash(unsigned_tx_out_idx, signature_type=SIGHASH_ALL)
            new_script = solver(unsigned_tx_out.script, partial_hash, secret_exponent_for_public_pair_lookup.get, public_pair_compressed_for_hash160_lookup.get, SIGHASH_ALL)
            new_txs_in.append(TxIn(unsigned_tx_out.previous_hash, unsigned_tx_out.previous_index, new_script))
            if not verify_script(new_script, unsigned_tx_out.script, partial_hash, hash_type=0):
                raise ValidationFailureError("just signed script Tx %s TxIn index %d did not verify" % (b2h_rev(tx_in.previous_hash), unsigned_tx_out_idx))

        tx = Tx(self.version, new_txs_in, self.new_txs_out, self.lock_timestamp)
        return tx

    def validate_unsigned_tx_out(self, unsigned_tx_out_idx, possible_solution):
        """Checks the transaction Tx signatures for validity. If invalid, raises a ValidationFailureError.
        tx_out_db: lookup of (hash, idx) => tx_out"""

        partial_hash = self.partial_hash(unsigned_tx_out_idx, signature_type=SIGHASH_ALL)
        if not verify_script(possible_solution, self.unsigned_txs_out[unsigned_tx_out_idx].script, partial_hash, hash_type=0):
            previous_hash = self.unsigned_txs_out[unsigned_tx_out_idx].previous_hash
            previous_index = self.unsigned_txs_out[unsigned_tx_out_idx].previous_index
            raise ValidationFailureError("Tx %s TxIn index %d script did not verify" % (b2h_rev(previous_hash), previous_index))

    def validate_unsigned_txs_out(self, possible_solutions):
        for unsigned_tx_out_idx, possible_solution in enumerate(possible_solutions):
            self.validate_unsigned_tx_out(unsigned_tx_out_idx, possible_solution)

    def validate_with_tx(self, tx):
        self.validate_unsigned_txs_out(tx_in.script for tx_in in tx.txs_in)
