"""
PowAlgorithm.py: contains the PowAlgorithm class.

"""

import hashlib, struct

class PowAlgorithm(object):
    """
    Represents a Strategy pattern object for doing proof-of-work under some
    scheme. Can do work on an item to a given target (lower is harder) and
    produce a nonce, verify that a nonce meets a given target for an item.
    Defines the hash function.
    
    """
    
    def __init__(self):
        """
        Make a new PowAlgorithm. Nothing to do, really.
        
        """
        pass
        
    def hash(self, data, nonce):
        """
        Given a byte string of data (i.e. the thing that you are trying to prove
        work on, which ought to be a hash) and a nonce integer of 8 bytes (the
        value which may or may not constitute proof of work), compute the hash
        that you get by hashing them both together (a string of bytes). This
        will be compared against the target to see if this nonce is a valid
        proof of work on this data at this target difficulty.
        
        To change the proof of work function, override this.
        
        Cribbed from the BitMessage source.
        """
        
        # By default, we'll use double-SHA512 of the nonce, then the data. This
        # is what BitMessage uses, which is where we stole the code from.
        return hashlib.sha512(hashlib.sha512(struct.pack('>Q', nonce) + 
            data).digest()).digest()

    def do_work(self, target, data):
        """
        Given a target bytestring (lower is harder) and a byte string of data to
        work on (probably a hash), find a nonce that, when hashed with the data,
        gives a hash where the first 8 bytes are less than the target. Returns
        that nonce.
        
        This function blocks until proof of work is completed, which may be some
        time.
        
        """
        
        # This holds the current nonce we're trying. When we get one that's good
        # enough, we return it.
        nonce = 0
        
        while not self.verify_work(target, data, nonce):
            # Keep trying nonces until we get one that works.
            nonce += 1
            
        # We found a good enough nonce! Return it; it is our proof of work.
        return nonce
    
    def do_some_work(self, target, data, placeholder=0, iterations=10000):
        """
        Do some work towards finding a proof of work on the data that meets (is
        less than) the target. Returns True and a valid nonce if it succeeds, of
        False and a placeholder value to be passed back on the next call if it
        doesn't find one in fewer than iterations iterations.
        
        Lets you do proof of work inside an event loop.
        """
        
        # This holds the nonce we're trying
        nonce = placeholder
        
        while nonce < placeholder + iterations:
            # TODO: overflow?
            if self.verify_work(target, data, nonce):
                # We solved a block! Hooray!
                return True, nonce
            nonce += 1
        
        # We haven't solved a block, but start from here next time.
        return False, nonce
    
    def verify_work(self, target, data, nonce):
        """
        Returns True if the given nonce represents at least target work on the
        given data, or False if it is invalid. Lower targets are harder.
        
        This is used both to verify received blocks and check if we've succeeded
        in proving work for new ones.
        
        """
        
        # Return whether it's low enough. We do string comparison on
        # bytestrings.
        return self.hash(data, nonce) <= target
