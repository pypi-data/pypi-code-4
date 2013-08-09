"""
Block.py: contains the Block class.

"""

import hashlib, struct, time

import pybc.util

class Block(object):
    """
    Represents a block in a blockchain. Can hold some data and calculate its own
    hash.
    
    """
    
    def __init__(self, payload, previous_hash, target, height, timestamp=None, 
        nonce=None):
        """
        Make a new block wrapping the given payload, with the given previous
        block hash bytestring and current target bytestring, at the given
        height. The payload must be a string, and ought not to be pickled,
        because unpickling it wouldn't be safe.
        
        timestamp is the time stamp for the block (8-byte unsigned seconds since
        epoch). If not specified, the current time is used.
        
        nonce, if specified, is a nonce value that purportedly meets the proof
        of work requirements for this block.
        
        """
        
        # Save the payload
        self.payload = payload
        
        # And the previous hash
        self.previous_hash = previous_hash
        
        # And the target that this block is supposed to meet
        self.target = target
        
        # And the height of this block (0 = the genesis block)
        self.height = height
        
        if timestamp is not None:
            # Use the specified timestamp
            self.timestamp = timestamp
        else:
            self.timestamp = int(time.time())
        
        # Hash the payload, previous hash, target, and timestamp together and
        # save that as a byte string. This isn't the hash of the whole block;
        # that hash (the sort of hash we reference with previous_hash) includes
        # the nonce. This also isn't sent over the wire or saved. This is,
        # however, what we have to prove work on.
        self.data_hash = hashlib.sha512(self.payload + self.previous_hash +
            self.target + struct.pack(">Q", self.height) + 
            struct.pack(">Q", self.timestamp)).digest()
        
        # Store the nonce if specified, or None if we still need to find a valid
        # nonce.
        self.nonce = nonce
        
    def to_bytes(self):
        """
        Return the block as a byte string. Including the nonce, which must be
        filled in.
        
        """
        
        # A block is a sequence of bytes with a header and a payload.
        # The header has:
        # The hash of the previous block (SHA-512, 64 bytes)
        # The target that this block has to meet (64 bytes)
        # The nonce used to meet it (8 bytes)
        # The rest of the block is the payload (of unspecified length)
        
        return "".join([self.previous_hash, self.target, 
            struct.pack(">Q", self.height), struct.pack(">Q", self.timestamp), 
            struct.pack('>Q', self.nonce), self.payload])
            
    @classmethod
    def from_bytes(cls, bytestring):
        """
        Make a new Block from the given bytestring. Uses the entire bytestring.
        
        Returns the Block, or None if the block could not be unpacked.
        
        """
        try:
        
            # Define the layout for the data we're unpacking: two 64-byte
            # strings (previous hash and target), followed by four 8-byte
            # unsigned integers (height, timestamp, and nonce)
            layout = ">64s64sQQQ"
        
            # Unpack the block header
            previous_hash, target, height, timestamp, nonce = \
                struct.unpack_from(layout, bytestring)
            
            # Get the payload, which comes after the header and runs to the end
            # of the block
            payload = bytestring[struct.calcsize(layout):]
            
            # Make a new block with everything filled in
            block = cls(payload, previous_hash, target, height, 
                timestamp=timestamp, nonce=nonce)
                
            # Give it back as our deserialized block
            return block
            
        except:
            # Block is invalid and could not be unpacked
            return None
        
        
    def block_hash(self):
        """
        Hash the whole block (including the nonce, which must be filled in)
        to get the block's full hash, as referenced by other blocks.
        """
        
        return hashlib.sha512(self.to_bytes()).digest()
        
        
    def do_work(self, algorithm):
        """
        Fill in the block's nonce by doing proof of work sufficient to meet the
        block's target (lower is harder) using the given PowAlgorithm. Fills in
        the block's nonce.
        
        """

        # Fill in the nonce
        self.nonce = algorithm.do_work(self.target, self.data_hash)
    
    def do_some_work(self, algorithm, iterations=10000):
        """
        Try to fill in the block's nonce, starting from the given placeholder,
        and doing at most the given number of iterations.
        
        Returns True if we succeed, or False if we need to run again.
        """
        
        if self.nonce is None:
            self.nonce = 0
        
        # Run the algorithm
        success, self.nonce = algorithm.do_some_work(self.target, 
            self.data_hash, placeholder=self.nonce, iterations=iterations)
            
        # TODO: we will pretend to be solved when we aren't in __str__, since we
        # set nonce to a number.
        
        # Return whether we succeeded
        return success
        
        
    def verify_work(self, algorithm):
        """
        Returns True if the block's currently set nonce is sufficient to meet
        the block's filled-in target under the given algorithm.
        
        This does not mean that the block is valid: you still need to make sure
        the block's payload is legal, and that the target the block uses is
        correct.
        
        """
        
        # Just ast the algorithm if the nonce is good enough for the target, on
        # our data_hash.
        return algorithm.verify_work(self.target, self.data_hash, self.nonce)
        
    def get_work(self, algorithm):
        """
        Returns the hash value that must be below target for this block to be
        valid. Mainly for debugging. Nonce must be filled in.
        
        """
        
        return algorithm.hash(self.data_hash, self.nonce)
        
    def __str__(self):
        """
        Print this block in a human-readable form.
        
        """
        
        # This holds all the lines we want to include
        lines = []
        
        if self.nonce is None:
            # Block hasn't been solved yet
            lines.append("----UNSOLVED BLOCK----")
        else:
            lines.append("----SOLVED BLOCK----")
            lines.append("Nonce: {}".format(self.nonce))
            lines.append("Block hash: {}".format(
                pybc.util.bytes2string(self.block_hash())))
        
        lines.append("Height {}".format(self.height))
        lines.append("Previous hash: {}".format(
            pybc.util.bytes2string(self.previous_hash)))
        
        # Block hash isn't less than target. The hash of the block hash and the
        # nonce under the blockchain's POW algorithm is less than target. So
        # don't line them up and be misleading.
        lines.append("Target: {}".format("".join("{:02x}".format(ord(char)) 
            for char in self.target)))
        lines.append("Timestamp: {}".format(pybc.util.time2string(
            self.timestamp)))
        # Encode the payload's special characters. TODO: Not available in Python
        # 3
        lines.append("Payload: {}".format(self.payload.encode(
            "string_escape")))
        lines.append("Data hash: {}".format(pybc.util.bytes2string(
            self.data_hash)))
        
        return "\n".join(lines)
