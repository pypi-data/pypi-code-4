"""
TransactionalBlockchain.py: contains the TransactionalBlockchain class.

"""

import hashlib, traceback, struct

from pybc.Blockchain import Blockchain
from pybc.transactions import pack_transactions, unpack_transactions
from pybc.transactions import InvalidPayloadError

class TransactionalBlockchain(Blockchain):
    """
    A Blockchain where the Blocks are just lists of transactions.
    
    """
    
    def verify_payload(self, next_block):
        """
        Verify the payload by verifying all the transactions in this block's
        payload against the parent block of this block.
        
        """
        
        # Probably don't need to lock or this.
        
        try:
        
            # This is a list of verified transactions to verify subsequent
            # transactions in the block against.
            verified_transactions = []
            
            if self.has_block(next_block.previous_hash):
                # This holds the block that this block is based on, or None if
                # it's a genesis block.
                parent_block = self.get_block(next_block.previous_hash)
            else:
                parent_block = None
            
            for transaction in unpack_transactions(next_block.payload):
                if not self.verify_transaction(transaction, parent_block,
                    other_transactions=verified_transactions):
                    # We checked the the next transaction against the blockchain and
                    # all previous transactions in the block.
                    
                    # This transaction is invalid
                    return False
                    
                # If we get here, this transaction is valid. Put it in the list.
                verified_transactions.append(transaction)
            
            # We have now verified all the the transactions in this block.
            return True
            
        except InvalidPayloadError:
            # Parsing the transactions broke, so the payload is invalid.
            return False
        
    def add_block(self, next_block):
        """
        Add the given block, or raise an exception.
        
        After adding the block, remove all transactions in it from our
        transaction queue.
        
        Also, drop any queued transactions that are now invalid.
        
        """
        
        with self.lock:
        
            super(TransactionalBlockchain, self).add_block(next_block)
            
            for transaction in unpack_transactions(next_block.payload):
                
                # Hash the transaction
                transaction_hash = hashlib.sha512(transaction).digest()
                
                if self.transactions.has_key(transaction_hash):
                    # We added this transaction, so take it out of the queue.
                    del self.transactions[transaction_hash]
                    
            # Make a new dict of queued transactions that are all valid in the
            # new blockchain
            new_transactions = {}
                    
            for transaction_hash, transaction in self.transactions.iteritems():
                # Go through all the queued transactions.
                
                if self.verify_transaction(transaction, self.highest_block, 
                    other_transactions=new_transactions.values()):
                    
                    # This transaction is still valid with the new blockchain
                    # and with all the other transactions in the new queue. Keep
                    # it in the new queue.
                    new_transactions[transaction_hash] = transaction
            
            # Now all the transactions in the new queue are valid. Replace the
            # old queue.
            self.transactions = new_transactions

