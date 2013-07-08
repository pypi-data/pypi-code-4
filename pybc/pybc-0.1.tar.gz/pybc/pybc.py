"""
pybc: generic blockchain library.

PyBC implements a blockchain distributed data structure, much like the one that
powers Bitcoin. A Blockchain is simply a list of payload-carrying Blocks. Each
Block includes the hash of the previous block, a data payload that can be
verified as permitted given the contents of all previous blocks, and a proof of
work that must meet some standard.

"""

import hashlib, struct, time, shelve, traceback, base64, itertools, random
import threading, collections, math, binascii

from twisted.internet import protocol, reactor, endpoints
from twisted.protocols.basic import LineReceiver

def bytes2string(bytestring):
    """
    Encode the given byte string as a text string. Returns the encoded string.
    
    """
    
    return base64.b64encode(bytestring)
    
def string2bytes(string):
    """
    Decode the given printable string into a byte string. Returns the decoded
    bytes.
    
    """
    
    return base64.b64decode(string)

def bytes2hex(bytestring):
    """
    Encode the given bytestring as hex.
    
    """
    
    return "".join("{:02x}".format(ord(char)) for char in bytestring)
    
def bytes2long(s):
    """
    Decode a Python long integer (bigint) from a string of bytes.
    
    See http://bugs.python.org/issue923643
    
    """
    return long(binascii.hexlify(s), 16)

def long2bytes(n):
    """
    Encode a Python long integer (bigint) as a string of bytes.
    
    See http://bugs.python.org/issue923643
    
    """
    
    hexstring = "%x" % n
    
    if len(hexstring) % 2 != 0:
        # Pad to even length, big-endian.
        hexstring = "0" + hexstring
    
    return binascii.unhexlify(hexstring)

def time2string(seconds):
    """
    Given a seconds since epock int, return a UTC time string.
    
    """
    
    return time.strftime("%d %b %Y %H:%M:%S", time.gmtime(seconds))

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
                bytes2string(self.block_hash())))
        
        lines.append("Height {}".format(self.height))
        lines.append("Previous hash: {}".format(
            bytes2string(self.previous_hash)))
        
        # Block hash isn't less than target. The hash of the block hash and the
        # nonce under the blockchain's POW algorithm is less than target. So
        # don't line them up and be misleading.
        lines.append("Target: {}".format("".join("{:02x}".format(ord(char)) for char 
            in self.target)))
        lines.append("Timestamp: {}".format(time2string(self.timestamp)))
        # Encode the payload's special characters. TODO: Not available in Python
        # 3
        lines.append("Payload: {}".format(self.payload.encode(
            "string_escape")))
        lines.append("Data hash: {}".format(bytes2string(self.data_hash)))
        
        return "\n".join(lines)

class State(object):
    """
    Represents some state data that gets kept up to date with the tip of the
    blockchain as new blocks come in. In Bitcoin, this might be used to hold the
    currently unspent outputs.
    
    Can return a copy of itself updated with a block forwards, or a copy of
    itself updated with a block backwards. Because we can run history both
    forwards and backwards, we can easily calculate the state at any block by
    walking a path from the tip of the longest branch.
    
    State objects are immutable.
    
    Ought to be replaced by implementations that actually keep state and make
    copies.
    
    """
    
    def step_forwards(self, block):
        """
        If this was the state before the given block, return a copy of what the
        state would be after the block.
        
        """
        
        # No change is possible, so just return ourselves.
        return self
        
    def step_backwards(self, block):
        """
        If this was the state after the given block, return a copy of what the
        state must have been before the block.
        
        """
        
        # No change is possible, so just return ourselves.
        return self
        
class Blockchain(object):
    """
    Represents a Blockchain that uses a particular PowAlgorithm. Starts with a
    genesis block (a block that has its previous hash set to 64 null bytes), and
    contains a list of blocks based on that genesis block. Responsible for
    verifying block payloads and that the rules respecting target updates are
    followed.
    
    We also keep an in-memory dict of transactions, represented as bytestrings.
    We include logic to verify transactions against the blockchain, but
    transactions are not actually put into blocks.
    
    We also keep a State that describes some collated state data over all
    previous blocks that new blocks might want to know about.
    
    """
    
    def __init__(self, algorithm, store_filename, initial_state=State()):
        """
        Given a PoW algorithm, a filename in which to store block data (which
        may get an extension appended to it), and an initial State object to use
        if none can be loaded from the file, construct a Blockchain.
        
        """
        
        # Set up our retargeting logic. We retarget so that it takes
        # retarget_time to generate retarget_period blocks. This specifies a 1
        # minute blocktime.
        self.retarget_time = 600
        self.retarget_period = 10
        
        # Keep the PowAlgorithm around
        self.algorithm = algorithm
        
        # Keep a shelve module database of all blocks by block hash.
        self.blockstore = shelve.open(store_filename)
        
        # Keep the highest Block around, so we can easily get the top of the
        # highest fork.
        self.highest_block = None
        
        # We keep the highest block's hash in the blockstore under "highest"
        if self.blockstore.has_key("highest"):
            self.highest_block = self.blockstore[self.blockstore["highest"]]
        
        # Keep a list of block hashes by height in our current fork, for
        # efficient access by height.
        self.hashes_by_height = []
        
        # We keep that in the blockstore too
        if self.blockstore.has_key("hashes_by_height"):
            self.hashes_by_height = self.blockstore["hashes_by_height"]
            
        # We need a lock so we can be a monitor and thus thread-safe
        self.lock = threading.RLock()
        
        # This is a dict of lists of pending blocks by the hash we need to
        # verify them.
        self.pending_on = collections.defaultdict(list)
        
        # This is a dict of callbacks by pending block hash
        self.pending_callbacks = {}
        
        # This holds our pending transactions as bytestrings by hash.
        self.transactions = {}
        
        # This keeps the State at the tip of the longest fork. If we don't find
        # a saved State, use the one provided. Its type determines the methods
        # we use to maintain state.
        self.state = initial_state
        if self.blockstore.has_key("state"):
            # Load the saved State.
            self.state = self.blockstore["state"]

    def has_block(self, block_hash):
        """
        Return True if we have the given block, and False otherwise.
        
        """
        
        # No need to lock since Python makes this atomic.
        return self.blockstore.has_key(block_hash)

    def get_block(self, block_hash):
        """
        Return the block with the given hash. Raises an error if we don't have
        it.
        
        """
        
        # No need to lock since Python makes this atomic.
        return self.blockstore[block_hash]


    def get_block_locator(self):
        """
        Returns a list of block hash bytestrings starting with the most recent
        block in the longest chain and going back, with exponentially fewer
        hashes the futher back we go. However, we make sure to include the 10
        most recent blocks.
        
        """
        
        # We do need to lock because this is a complicated traversal. We can't
        # for example, switch threads in the middle of this.
        with self.lock:
        
            # This holds the list of hashes we use
            locator = []
            
            # This holds the step we use for how far to go back after including
            # each block.
            step = 1
            
            # This holds our position in the longest chain, from the genesis
            # block
            position = len(self.hashes_by_height) - 1
            
            while position > 0:
                # Grab the hash
                locator.append(self.hashes_by_height[position])
                
                # Go back by the recommended step
                position -= step
                
                if len(locator) > 10:
                    # After the 10 most recent hashes, start doubling the step
                    # size.
                    step *= 2
            
            # Always include the genesis block, if available
            if len(self.hashes_by_height) > 0:
                locator.append(self.hashes_by_height[0])
              
            return locator
                

    def blocks_after_locator(self, locator_hashes):
        """
        Takes a "block locator" in the form of a list of hashes. The first
        hash is the most recent block that another node has, and subsequent
        hashes in the locator are the hashes of earlier blocks, with exponential
        backoff.
        
        We proceed back through our longest fork until we find a block that the
        remote node mentions (or we get to the genesis block), and return a list
        of the hashes of each of the blocks proceeding upwards from there, in
        forward order.
        
        """
        
        # Complicated traversal: need to lock.
        with self.lock:
        
            # Process the locator hashes into a set for easy membership checking
            mentioned = set(locator_hashes)
            
            # This holds whether we found a block they mentioned. If we do find
            # one, we can update them from there. If not, we will have to start
            # from our genesis block.
            found = False
            
            for block_hash, index_from_end in enumerate(reversed(
                self.hashes_by_height)):
                
                # Go through the longest chain backwards
                if block_hash in mentioned:
                    # This block was mentioned by them. We can update them from
                    # here.
                    found = True
                    break
            
            if found:
                # Get the index from the start of the list of the earliest block
                # they have not heard of (the block after index_from_end).
                # Because of Python indexing, we don't need to add 1 here.
                index = len(self.longest_chain) - index_from_end
            else:
                # Start from our genesis block. We didn't find anything they
                # mentioned.
                index = 0
            
            # Return a list of all the hashes from that point onwards
            return self.hashes_by_height[index:]
        
    def make_block(self, payload):
        """
        Create a block that would, if solved, add the given payload onto the
        longest chain.
        
        Does not verify the payload.
        
        """
        
        with self.lock:
        
            if self.highest_block is None:
                # This has to be a genesis block
                new_block = Block(payload, "\0" * 64, 
                    self.next_block_target(None), 0)
            else:
                # We're adding on to an existing chain.
                
                # Even if our clock is behind the timestamp of the block, don't
                # try to generate a block timestamped older than the parent
                # block, because that would be invalid.
                min_timestamp = self.highest_block.timestamp
                
                new_block = Block(payload, self.highest_block.block_hash(), 
                    self.next_block_target(self.highest_block), 
                    self.highest_block.height + 1,
                    timestamp=max(int(time.time()), min_timestamp))
        
            
            return new_block
    
    def can_verify_block(self, next_block):
        """
        Return True if we can determine whether the given block is valid, based
        on the blocks we already have. Returns False if we don't have the parent
        blocks needed to verify this block.
        
        """
        
        # No need to lock here. Nothing fancy.
        
        if next_block.height == 0:
            # It's a genesis block. We can always check those.
            return True
        
        # The block store never contains any blocks we can't verify, so if we
        # have the parent, we can verify this block.
        return self.blockstore.has_key(next_block.previous_hash)
        
    def verify_block(self, next_block):
        """
        Return True if the given block is valid based on the parent block it
        references, and false otherwise. We can't just say new blocks are
        invalid if a longer chain exists, though, because we might be getting a
        new chain longer than the one we have.
        
        Do not call this unless can_verify_block() is true for the block.
        
        You probably want to override verify_payload instead of this.
        
        """
        
        with self.lock:
        
            if ((next_block.height == 0 ) != 
                (next_block.previous_hash == "\0" * 64)):
                # Genesis blocks must have height 0 and a previous hash of all
                # 0s. If we have exactly one of those things, the block is
                # invalid.
                print "Genesis block height and hash are mismatched."
                return False
            
            # Get the previous block, or None if this is a genesis block
            previous_block = None
            if next_block.height != 0:
                # This isn't a genesis block, so load its parent, which we must
                # have. (Otherwise can_verify_block would be false.)
                previous_block = self.blockstore[next_block.previous_hash]
            
            now = int(time.time())
            if next_block.timestamp > (now + 10 * 60):
                # The block is from more than 10 minutes in the future.
                print "Block is from too far in the future: {} vs {}".format(
                    time2string(next_block.timestamp), time2string(now))
                return False
            
            if (previous_block is not None and 
                previous_block.timestamp > next_block.timestamp):
                # The block is trying to go back in time.
                print "Block is timestamped earlier than parent."
                return False
                
            if (previous_block is not None and 
                next_block.height != previous_block.height + 1):
                # The block is not at the correct height (1 above its parent)
                print "Block height incorrect."
                return False
            
            if next_block.target != self.next_block_target(previous_block):
                # The block isn't valid if it cheats at targeting.
                print "Block target incorrect. Should be {}".format(
                    bytes2hex(self.next_block_target(previous_block)))
                return False
            
            if not next_block.verify_work(self.algorithm):
                # The block also isn't valid if the PoW isn't good enough
                print "Block PoW isn't correct."
                return False
            
            if not self.verify_payload(next_block):
                # The block can't be valid if the payload isn't.
                print "Block payload is invalid."
                return False
                
            # Block is valid
            return True
            
    def verify_payload(self, next_block):
        """
        Return True if the payload of the given next block is valid, and false
        otherwise.
        
        Should be overridden to define payload logic. The default implementation
        accepts any payloads.
        
        """
        
        return True
        
    def next_block_target(self, previous_block):
        """
        Get the PoW target (64 bytes) that the next block must use, based on the
        given previous block Block object (or None).
        
        Should be overridden to define PoW difficulty update logic.
        """
        
        # We don't need to lock, but most overrides will.
        
        if previous_block is None:
            # No blocks yet, so this is the starting target. You get a 0 bit as
            # the first bit instead of a 1 bit every other hash. So to get n
            # leading 0 bits takes on average 2^n hashes. n leading hex 0s takes
            # on average 16^n hashes.
            return struct.pack(">Q", 0x00000fffffffffff) + "\xff" * 56
        else:
            # Easy default behavior: re-target every 10 blocks to a rate of 10
            # block per minute, but don't change target by more than 4x/0.25x
            
            if (previous_block.height > 0 and 
                previous_block.height % self.retarget_period == 0):
                # This is a re-target block. It's on a multiple of
                # retarget_period and not the genesis block.
                
                # Go get the time of the block retaregt_preiod blocks ago
                block = previous_block
                for _ in xrange(self.retarget_period):
                    # Go back a block retarget_period times.
                    # We always have all the blocks, so this will work.
                    block = self.blockstore[block.previous_hash]
                    
                old_time = block.timestamp
                new_time = previous_block.timestamp
                
                # We want new_time - old_time to be retarget_time seconds.
                time_taken = new_time - old_time
                ideal_time = self.retarget_time
                
                print "{} blocks took {}, should have taken {}".format(
                    self.retarget_period, time_taken, ideal_time)
                    
                # At constant hashrate, the generation rate scales linearly with
                # the target. So if we took a factor of x too long, increasing
                # the target by a factor of x should help with that.
                factor = float(time_taken) / ideal_time
                
                print "Want to scale generation rate by {}".format(factor)
                
                # Don't scale too sharply.
                if factor > 4:
                    factor = 4
                if factor < 0.25:
                    factor = 0.25
                
                print "Will actually scale by: {}".format(factor)
                
                # Load the target as a big int
                old_target = bytes2long(previous_block.target)
                
                print "{} was old target".format(bytes2hex(
                    previous_block.target))
                
                # Multiply it
                new_target = long(old_target * factor)
                
                print "new / old = {}".format(new_target / old_target)
                print "old / new = {}".format(old_target / new_target)
                
                new_target_bytes = long2bytes(new_target)
                
                while len(new_target_bytes) < 64:
                    # Padd to the appropriate length with nulls
                    new_target_bytes = "\0" + new_target_bytes
                if len(new_target_bytes) > 64:
                    # New target would be too long. Don't change
                    print "No change because new target is too long."
                    return previous_block.target
                
                print "{} is new target".format(bytes2hex(new_target_bytes))
                    
                return new_target_bytes
                
            else:
                # If it isn't a retarget, don't change the target.
                return previous_block.target
    
    def switch_forks(self, new_tip):
        """
        Switch forks from the current fork in self.highest_block and
        self.hashes_by_height to the one with the tip Block new_tip. The new
        fork must be higher than the old one.
        
        Make sure self.hashes_by_height has all the hashes of the blocks
        on the new fork, and that these changes are sent to the blockstore.
        
        Also, change our State and send that to the blockstore.
        
        This function makes changes to the blockstore, so the caller should
        probably sync it.
        
        """
        
        # Strategy:
        # Change our State.
        # Find the common ancestor of highest_block and new_tip
        # Make sure hashes_by_height has enough spots
        # Fill them in from new_tip back to the common ancestor.
        
        # This is incredibly complicated
        with self.lock:
        
            # Switch states. TODO: This finds the common ancestor too
            self.state = self.state_after(new_tip)
            # Put the new State in the blockstore.
            self.blockstore["state"] = self.state
        
            # Find the common ancestor 
            ancestor = self.common_ancestor(new_tip, self.highest_block)
        
            if ancestor is None:
                # Go back through the whole list, replacing the genesis block.
                ancestor_height = -1
            else:
                # Go back only to the height after the common ancestor.
                ancestor_height = ancestor.height
        
            # Make sure hashes_by_height is big enough
            
            while len(self.hashes_by_height) <= new_tip.height:
                # Make empty spots in the hashes by height list until
                # hashes_by_height[new_tip.height] is a valid location.
                self.hashes_by_height.append(None)
            
            # Now go back through the blocks in the new fork, filling in
            # hashes_by_height.
            
            # This holds the block we are to put in next
            position = new_tip
            
            while position is not None and position.height > ancestor_height:
                # For every block on the new fork back to the common ancestor,
                # stick its hash in the right place in hashes by height.
                self.hashes_by_height[position.height] = position.block_hash()
                
                if position.previous_hash != "\0" * 64:
                    # Go back to the previous block and do it
                    position = self.blockstore[position.previous_hash]
                else:
                    # We've processed the genesis block and are done.
                    position = None
                    
            # Save our hashes by height changes to the blockstore.
            self.blockstore["hashes_by_height"] = self.hashes_by_height
    
    def queue_block(self, next_block, callback=None):
        """
        We got a block that we think goes in the chain, but we may not have all
        the previous blocks that we need to verify it yet.
        
        Put the block into a receiving queue.
        
        If the block is eventually verifiable, call the callback with the hash
        and True if it's good, or the hash and False if it's bad.
        
        """
        
        with self.lock:
            
            # This is the stack of hashes that we have added to the blockchain.
            # We need to check what blocks are wauiting on them.
            added_hashes = []
            
            if self.can_verify_block(next_block):
                # We can verify it right now
                if self.verify_block(next_block):
                    # The block is good!
                    self.add_block(next_block)
                    
                    if callback is not None:
                        callback(next_block.block_hash(), True)
                    
                    print "Block height {} immediately verified: {}".format(
                        next_block.height,
                        bytes2string(next_block.block_hash()))
                    
                    # Record that we added the block
                    added_hashes.append(next_block.block_hash())
                else:
                    print "Invalid block:\n{}".format(next_block)
                    if callback is not None:
                        callback(next_block.block_hash(), False)
            else:
                # Add this block to the pending blocks
                self.pending_on[next_block.previous_hash].append(next_block)
                self.pending_callbacks[next_block.block_hash()] = callback
                
                print "Block height {}, hash {} pending on parent {}".format(
                        next_block.height,
                        bytes2string(next_block.block_hash()), 
                        bytes2string(next_block.previous_hash))
            
            while len(added_hashes) > 0:
                # There are blocks that we have added, but we haven't checked
                # for other blocks pending on them. Do that.
                
                # Pop off a hash to check
                hash_added = added_hashes.pop()
                
                # Get the list of waiters
                waiters = self.pending_on[hash_added]
                
                # Remove it
                del self.pending_on[hash_added]
                
                print "{} waiters were waiting on {}".format(len(waiters), 
                    bytes2string(hash_added))
                    
                for waiter in waiters:
                    # We ought to be able to verify and add each waiter.
                    
                    # Get the callback
                    waiter_callback = self.pending_callbacks[
                        waiter.block_hash()]
                    
                    # Remove it from the collection of remaining callbacks
                    del self.pending_callbacks[waiter.block_hash()]
                
                    if self.can_verify_block(waiter):
                        # We can verify the block right now (ought to always be
                        # true)
                        if self.verify_block(waiter):
                            # The block is good! Add it
                            self.add_block(waiter)
                            
                            if waiter_callback is not None:
                                # Call the callback
                                waiter_callback(waiter.block_hash(), True)
                            
                            print "Queued block height {} verified: {}".format(
                                waiter.height,
                                bytes2string(waiter.block_hash()))
                            
                            # Record that we added the pending block, so things
                            # pending on it can now be added
                            added_hashes.append(waiter.block_hash())
                        else:
                            # TODO: throw out blocks waiting on invalid blocks.
                            # If we have any of those, there's probablt a hard
                            # fork.
                            
                            print "Queued block invalid: {}".format(
                                bytes2string(waiter.block_hash()))
                            
                            if waiter_callback is not None:
                                # Call the callback
                                waiter_callback(waiter.block_hash(), False)
                    else:
                        # This should never happen
                        print("Couldn't verify a waiting block when its parent "
                            "came in!")
    
    def state_after(self, block):
        """
        Given that our State is currently up to date with our current
        highest_block, return a State that is in effect after the given block.
        
        block may not be None.
        
        Walks the blockchain from the tip of the highest fork to the given
        block, which must be in the block store.
        
        """
        
        with self.lock:
        
            if block == self.highest_block:
                # We already have the state after this
                return self.state
        
            if self.highest_block is None:
                # Easy case: this must be a genesis block.
                # Return the state updated with the new block
                return self.state.step_forwards(block)
            
            # If we get here, we know we have a highest block, and that we need
            # to walk from there to the block we're being asked about.
            
            # Find the common ancestor of this block and the tip, where we have
            # a known State.
            ancestor = self.common_ancestor(block, self.highest_block)
            
            if ancestor is None:
                # This block we want the state after is on a completely
                # different genesis block.
                
                # Go back until the state after nothing, and then go forward
                # again.
                ancestor_hash = "\0" * 64
            else:
                # Go back until the state after the common ancestor, and then go
                # forward again.
                ancestor_hash = ancestor.block_hash()
                
            # Walk the State back along the longest fork to the genesis block.
            # TODO: Is there a more efficient way to do this?
            
            # This holds our scratch state
            state = self.state
            
            # This holds the hash of the block we're on
            position = self.highest_block.block_hash()
            
            while position != ancestor_hash:
                # Until we reach the common ancestor...
                
                # Undo the current block
                state = state.step_backwards(self.blockstore[position])
                
                # Step back a block
                position = self.blockstore[position].previous_hash
                
            # Now we've reverted to the post-common-ancestor state. TODO: Can't
            # we just get a known state here? Or can we save a state per tip?
            
            # Now apply all the blocks from there to block in forwards order.
            # First get a list of them
            blocks_to_apply = []
            
            position = block.block_hash()
            while position != ancestor_hash:
                # Collect the blocks on the path from block to the common
                # ancestor.
                blocks_to_apply.append(self.blockstore[position])
                
                # Step back a block
                position = self.blockstore[position].previous_hash
                
            # Flip the blocks that need to be applied into chronological order.
            blocks_to_apply.reverse()
            
            for block_to_apply in blocks_to_apply:
                # Apply the block to the state
                state = state.step_forwards(block_to_apply)
            
            # We've now updated to the state for after the given block.
            return state
        
        
            
    
    def genesis_block_for(self, block):
        """
        Return the genesis block for the given Block in the blockstore.
        
        """
        
        while block.previous_hash != "\0" * 64:
            # This isn't a genesis block. Go back.
            block = self.blockstore[block.previous_hash]
            
        return block                
        
    def common_ancestor(self, block_a, block_b):
        """
        Get the most recent common ancestor of the two Blocks in the blockstore,
        or None if they are based on different genesis blocks.
        
        Either block_a or block_b may be None, in which case the common ancestor
        is None as well.
        
        """
        
        # This is incredibly complicated
        with self.lock:
        
            if block_a is None or block_b is None:
                # Common ancestor with None is always None (i.e. different
                # genesis blocks).
                return None
        
            # This holds our position on the a branch.
            position_a = block_a.block_hash()
        
            # This holds all the hashes we visited tracing back from a
            hashes_a = set(position_a)
            
            # This holds our position on the b branch.
            position_b = block_b.block_hash()
        
            # This holds all the hashes we visited tracing back from b
            hashes_b = set(position_b)
            
            while position_a != "\0" * 64 or position_b != "\0" * 64:
                # While we haven't traced both branches back to independent
                # genesis blocks...
                if position_a != "\0" * 64:
                    # Trace the a branch back further, since it's not off the
                    # end yet.
                    
                    # Move back a step on the a branch
                    position_a = self.blockstore[position_a].previous_hash
                    hashes_a.add(position_a)
                
                    if position_a != "\0" * 64 and position_a in hashes_b:
                        # We've found a common ancestor. Return the block.
                        return self.blockstore[position_a]
                        
                if position_b != "\0" * 64:
                    # Trace the b branch back further, since it's not off the
                    # end yet.
                    
                    # Move back a step on the b branch
                    position_b = self.blockstore[position_b].previous_hash
                    hashes_b.add(position_b)
                
                    if position_b != "\0" * 64 and position_b in hashes_a:
                        # We've found a common ancestor. Return the block.
                        return self.blockstore[position_b]
                    
                    
                # We've hit independent genesis blocks. There is no common
                # ancestor, so return None.
                return None
    
    def add_block(self, next_block):
        """
        Add a block as the most recent block in the blockchain. The block must
        be valid, or an Exception is raised.
        
        """

        # This is complicated. Lock the blockchain
        with self.lock:

            if self.verify_block(next_block):
                # Put the block in the block store
                self.blockstore[next_block.block_hash()] = next_block
                
                if (self.highest_block is None or 
                    next_block.height > self.highest_block.height):
                    
                    # This new block is higher than the previously highest
                    # block.
                    
                    if (self.highest_block is not None and 
                        next_block.previous_hash != 
                        self.highest_block.block_hash()):
                            
                            # We had an old highest block, but we need to switch
                            # forks away from it.
                            
                            # This may involve replacing a big part of our
                            # hashes_by_height list and updating our State in a
                            # complex way. We have a function for this.
                            self.switch_forks(next_block)
                            
                    else:
                        # This is a direct child of the old highest block, or a
                        # new genesis block.
                        
                        # Put this block on the end of our hashes by height list
                        self.hashes_by_height.append(next_block.block_hash())
                        # And save that back to the blockstore too
                        self.blockstore["hashes_by_height"] = \
                            self.hashes_by_height
                            
                        # Update the State with a simple step
                        self.state = self.state.step_forwards(next_block)
                        # And save that back to the blockstore too
                        self.blockstore["state"] = self.state
                            
                    # Set the highest block to the new block.
                    self.highest_block = next_block
                    
                    # Put the new highest block's hash into the blockstore under
                    # "highest".
                    self.blockstore["highest"] = self.highest_block.block_hash()
                    
                    # Save the blockstore to disk
                    self.blockstore.sync()
            
                    # Now there is a new block on the longest chain. Throw out
                    # all transactions that are now invalid on top of it. First,
                    # make a list of them.
                    
                    # Note: Expect some console spam when debugging invalid
                    # transactions, which are only really expected here.
                    print "Dropping invalid queued transactions."
                    invalid_transaction_hashes = [hash for hash, transaction in 
                        self.transactions.iteritems() if not 
                        self.verify_transaction(transaction, 
                        self.highest_block)]
                        
                    # Then, remove them all
                    for transaction_hash in invalid_transaction_hashes:
                        del self.transactions[transaction_hash]   
                
            else:
                # Block we tried to add failed verification. Complain.
                raise Exception("Invalid block!")
            
    def longest_chain(self):
        """
        An iterator that goes backwards through the currently longest chain to
        the genesis block.
        
        """
        # Locking things in generators is perfectly fine, supposedly.
        with self.lock:
        
            # This is the block we are currently on
            current_block = self.highest_block
            if current_block is None:
                return
                
            yield current_block
            
            # This holds the hash of the prevous block
            previous_hash = current_block.previous_hash
            
            while previous_hash != "\0" * 64:
                # While the previous hash is a legitimate block hash, keep
                # walking back.
                current_block = self.blockstore[previous_hash]
                yield current_block
                previous_hash = current_block.previous_hash
    
    def verify_transaction(self, transaction_bytes, chain_head, 
        other_transactions=[]):
        """
        Returns True if the given transaction is valid, if the block chain_head
        is the current top-most block. Valid transactions are broadcast to
        peers, while invalid transactions are discarded.
        
        chain_head may be None, in which case we are asking if the transaction
        is valid in the genesis block.
        
        We need to be able to tell if a transaction is valid on non-longest
        forks, because otherwise we won't be able to verify transactions in
        blocks that are making up a fork that, once we get more blocks, will
        become the longest fork. (The default Blockchain implementation doesn't
        actually store transactions in blocks, but we need to have a design that
        supports it.)
        
        Along with verify_payload, subclasses probably ought to override this to
        specify application-specific behavior.
        
        other_transactions, if specified, is a list of previous transactions in
        the current block that this transaction needs to be checked against.
        
        """
        
        return True
    
    def transaction_valid_for_relay(self, transaction):
        """
        Returns True if we should accept transactions like the given transaction
        from peers, False otherwise.
        
        If you are making a system where block generators put special
        transactions into blocks, you don't want those transactions percolating
        through the network and stealing block rewards.
                
        """
        
        return True        
        
    def get_transaction(self, transaction_hash):
        """
        Given a transaction hash, return the transaction (as a bytestring) with
        that hash. If we don't have the transaction, return None instead of
        throwing an error (in case the transaction gets removed, perhaps by
        being added to a block).
        
        """
        with self.lock:
            if self.transactions.has_key(transaction_hash):
                return self.transactions[transaction_hash]
            else:
                return None
        
        
    def has_transaction(self, transaction_hash):
        """
        Return True if we have the transaction with the given hash, and False
        otherwise. The transaction may go away before you can call
        get_transaction.
        
        """
        
        # No need to lock. This is atomic.
        return self.transactions.has_key(transaction_hash)
        
        
    def add_transaction(self, transaction, callback=None):
        """
        Called when someone has a transaction to give to us. Takes the
        transaction as a string of bytes. Returns True if the transaction is
        valid, or False if the transaction is invalid or can't be verified (i.e.
        references non-downloaded blocks). Only transactions that are valid in
        light of currently queued transactions are acepted.
        
        Calls the callback, if specified, with the transaction's hash and its
        validity (True or False).
        
        We don't queue transactions waiting on the blocks they depend on, like
        we do blocks, because it doesn't matter if we miss having one.
        
        If the transaction is valid, we will remember it by hash.
        
        """
        
        with self.lock:
        
            # Hash the transaction
            transaction_hash = hashlib.sha512(transaction).digest()
            
            if self.verify_transaction(transaction, self.highest_block, 
                other_transactions=self.transactions.values()):
                # The transaction is valid in our current fork.
                # Keep it around.
                self.transactions[transaction_hash] = \
                    transaction
                
                # Notify the callback
                if callback is not None:
                    callback(transaction_hash, True)
            else:
                # The transaction is invalid.
                if callback is not None:
                    # Tell the callback
                    callback(transaction_hash, False)

class InvalidPayloadError(Exception):
    """
    Thrown when a transaction list can't be decoded.
    
    """

def unpack_transactions(block_payload):
    """
    Given a block payload, parse it out into its constituent transactions.
    Yield each of them.
    
    The encoding we use is
    <4 byte transaction count>
    [<4 byte transaction byte length>
    <transaction bytes>]*
    
    May throw an InvalidPayloadError if the payload is not a properly
    encoded list.
    
    """
    try:
        # How many transactions do we need?
        (transaction_count,) = struct.unpack(">I", block_payload[0:4])
        # Where should we start the next record from?
        location = 4
        
        for i in xrange(transaction_count):
            # How many bytes is the transaction?
            (transaction_length,) = struct.unpack(">I", 
                block_payload[location:location + 4])
            location += 4
                
            # Grab the transaction bytes
            transaction_bytes = block_payload[location:location + 
                transaction_length]
            location += transaction_length
            
            yield transaction_bytes    
    except GeneratorExit:
        # This is fine
        pass
    except:
        # We broke while decoding a transaction.
        traceback.print_exc()
        raise InvalidPayloadError
        
def pack_transactions(transactions):
    """
    Encode the given list of transactions into a payload.

    The encoding we use is
    <4 byte transaction count>
    [<4 byte transaction byte length>
    <transaction bytes>]*

    """

    # Make a list of transaction records with their lengths at the
    # front.
    transactions_with_lengths = [struct.pack(">I", len(transaction)) + 
        transaction for transaction in transactions]
    
    # Return the number of transaction records followed by the records.
    return (struct.pack(">I", len(transactions_with_lengths)) + 
        "".join(transactions_with_lengths))

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

class BlockchainProtocol(LineReceiver):
    """
    This is a Twisted protocol that exchanges blocks with the peer at the other
    end, and floods valid non-block messages. Used by both servers and clients.
    
    It is a line-oriented protocol with occasional blocks of raw data.
    
    """
    
    def __init__(self, factory, remote_address, incoming=False):
        """
        Make a new protocol (i.e. connection handler) belonging to the given
        Factory, which in turn belongs to a Peer.
        
        remote_address should be the (host, port) tuple of the host we are
        talking to.
        
        Incominc specifies whether this connection is incoming or not. If it's
        not incoming, the port they are using will be advertised. If incoming is
        true, this Protocol will kick off the connection by greeting the other
        peer.
        
        """
        
        # Keep the factory around, so we can talk to our Peer.
        self.factory = factory
        
        # Remember the address of the host we are talking to
        self.remote_address = remote_address
        
        # Remember if we're supposed to greet or not.
        self.incoming = incoming
        
    def connectionMade(self):
        """
        A connection has been made to the remote host. It may be a server or
        client.
        
        """
        
        print "Made a connection!"
        
        # Let the peer know we are connected.
        self.factory.peer.made_connection(self)
        
        if self.incoming:
            # They connected to us. Send a greeting, saying what network we're
            # in and our protocol version.
            self.send_message(["NETWORK",  self.factory.peer.network,
                self.factory.peer.version])
    
    def connectionLost(self, reason):        
        """
        This connection has been lost.
        """
        
        # We're no longer a connection that the peer should send things to.
        self.factory.peer.lost_connection(self)
        
        print "Protocol lost connection. Reason: ", reason
    
    def disconnect(self):
        """
        Drop the connection from the Twisted thread.
        
        """
        
        reactor.callFromThread(self.transport.loseConnection)
    
    def send_message(self, parts):
        """
        Given a message as a list of parts, send it from the Twisted thread.
        
        """
        
        # Compose the message string and send it from the Twisted thread
        reactor.callFromThread(self.sendLine, " ".join(map(str, parts)))
    
    def handle_message(self, parts):
        """
        Given a message as a list of string parts, handle it. Meant to run non-
        blocking in its own thread.
        
        Schedules any reply and any actions to be taken to be done in the main
        Twisted thread.
        """
        
        try: 
            if len(parts) == 0:
                # Skip empty lines
                return
            
            if parts[0] == "NETWORK":
                # This is a network command, telling us the network and version of
                # the remote host. If we like them (i.e. they are equal to ours),
                # send back an acknowledgement with our network info. Also start
                # requesting peers and blocks from them.
                
                if (parts[1] == self.factory.peer.network and 
                    int(parts[2]) == self.factory.peer.version):
                    # We like their network and version number.
                    # Send back a network OK command with our own.
                    self.send_message(["NETWORK-OK", self.factory.peer.network, 
                        self.factory.peer.version])
                        
                    # Ask them for peers
                    self.send_message(["GETADDR"])
                    
                    # Ask them for the blocks we need, given our list of block
                    # locator hashes.
                    self.send_message(["GETBLOCKS"] + 
                        [bytes2string(block_hash) for block_hash in 
                        self.factory.peer.blockchain.get_block_locator()])
                        
                    # Send all the pending transactions
                    for transaction_hash in \
                        self.factory.peer.blockchain.transactions.iterkeys():
                        
                        self.send_message(["TXINV", bytes2string(
                            transaction_hash)])
                        
                else:
                    # Nope, we don't like them.
                    
                    # Disconnect
                    self.disconnect()
                    
            elif parts[0] == "NETWORK-OK":
                # This is a network OK command, telling us that they want to
                # talk to us, and giving us their network and version number. If
                # we like their network and version number too, we can start
                # exchanging peer info.
                
                if (parts[1] == self.factory.peer.network and 
                    int(parts[2]) == self.factory.peer.version):
                    
                    # We like their network and version number. Send them a
                    # getaddr message requesting a list of peers. The next thing
                    # they give us might be something completely different, but
                    # that's OK; they ought to send some peers eventually.
                    self.send_message(["GETADDR"])
                    
                    # Ask them for the blocks we need, given our list of block
                    # locator hashes.
                    self.send_message(["GETBLOCKS"] + 
                        [bytes2string(block_hash) for block_hash in 
                        self.factory.peer.blockchain.get_block_locator()])
                        
                    # Send all the pending transactions
                    for transaction_hash in \
                        self.factory.peer.blockchain.transactions.iterkeys():
                        
                        self.send_message(["TXINV", bytes2string(
                            transaction_hash)])
                else:
                    # We don't like their network and version. Drop them.
                    
                    # Disconnect
                    self.disconnect()
                    
            elif parts[0] == "GETADDR":
                # They want a list of all known peers.
                # Send them ADDR messages, one per known peer.
                
                for host, port, time_seen in self.factory.peer.get_peers():
                    # Send the peer's host and port in an ADDR message
                    self.send_message(["ADDR", host, port, time_seen])
            elif parts[0] == "ADDR":
                # They claim that there is a peer. Tell our peer the host and port
                # and time seen.
                self.factory.peer.peer_seen(parts[1], int(parts[2]), 
                    int(parts[3]))
            elif parts[0] == "GETBLOCKS":
                # They gave us a block locator. Work out the blocks they need,
                # and send INV messages about them.
                
                # Decode all the hex hashes to bytestring
                block_hashes = [string2bytes(part) for part in parts[1:]]
                
                for needed_hash in \
                    self.factory.peer.blockchain.blocks_after_locator(
                    block_hashes):
                    
                    # They need this hash. Send an INV message about it.
                    # TODO: consolidate and limit these.
                    self.send_message(["INV", bytes2string(needed_hash)])
            elif parts[0] == "INV":
                # They have a block. If we don't have it, ask for it.
                
                # TODO: allow advertising multiple things at once.
                
                # Decode the hash they have
                block_hash = string2bytes(parts[1])
                
                if not self.factory.peer.blockchain.has_block(block_hash):
                    # We need this block!
                    self.send_message(["GETDATA", parts[1]])
                    
            elif parts[0] == "GETDATA":
                # They want the data for a block. Send it to them if we have
                # it.
                
                # Decode the hash they want
                block_hash = string2bytes(parts[1])
                
                if self.factory.peer.blockchain.has_block(block_hash):
                    # Get the block to send
                    block = self.factory.peer.blockchain.get_block(block_hash)
                    
                    # Send them the block. TODO: This encoding is terribly
                    # inefficient, but we can't send it as binary without them
                    # switching out of line mode, and they don't know to do that
                    # because messages queue.
                    self.send_message(["BLOCK", bytes2string(block.to_bytes())])
                else:
                    print "Can't send missing block: '{}'".format(
                        bytes2string(block_hash))
            
            elif parts[0] == "BLOCK":
                # They have sent us a block. Add it if it is valid.
                
                # Decode the block bytes
                block_bytes = string2bytes(parts[1])
                
                # Make a Block object
                block = Block.from_bytes(block_bytes)
                
                print "Decoded incoming block."
                
                # Give it to the blockchain to add when it can. If it does get
                # added, we announce it.
                self.factory.peer.send_block(block)
            elif parts[0] == "TXINV":
                # They have sent us a hash of a transaction that they have. If
                # we don't have it, we should get it and pass it on.
                
                # Decode the hash they have
                transaction_hash = string2bytes(parts[1])
                
                if not self.factory.peer.blockchain.has_transaction(
                    transaction_hash):
                    
                    # We need this transaction!
                    self.send_message(["GETTX", parts[1]])
            elif parts[0] == "GETTX":
                # They want a transaction from our blockchain.
                
                # Decode the hash they want
                transaction_hash = string2bytes(parts[1])
                
                if self.factory.peer.blockchain.has_transaction(transaction_hash):
                    # Get the transaction to send
                    transaction = self.factory.peer.blockchain.get_transaction(
                        transaction_hash)
                    
                    if transaction is not None:
                        # We have it (still). Send them the block transaction.
                        self.send_message(["TX", bytes2string(transaction)])
                    else:
                      print "Lost transaction: '{}'".format(
                        bytes2string(transaction_hash))  
                else:
                    print "Can't send missing transaction: '{}'".format(
                        bytes2string(transaction_hash))
            elif parts[0] == "TX":
                # They have sent us a transaction. Add it to our blockchain.
                
                # Decode the transaction bytes
                transaction_bytes = string2bytes(parts[1])
                
                print "Incoming transaction."
                
                if self.factory.peer.blockchain.transaction_valid_for_relay(
                    transaction_bytes):
                    
                    # This is a legal transaction to accept from a peer (not
                    # something like a block reward).
                    print "Transaction acceptable from peer."
                
                    # Give it to the blockchain as bytes. The blockchain can
                    # determine whether to forward it on or not and call the
                    # callback with transaction hash and transaction status
                    # (True or False).
                    self.factory.peer.send_transaction(
                        transaction_bytes)
                  
            elif parts[0] == "ERROR":
                # The remote peer didn't like something.
                # Print debugging output.
                print "Error from remote peer: {}".format(" ".join(parts[1:]))
            
            else:
                # They're trying to send a command we don't know about.
                # Complain.
                print "Remote host tried unknown command {}".format(parts[1])
                self.send_message(["ERROR", parts[0]])
            
            if not self.incoming:    
                # We processed a valid message from a peer we connected out to.
                # Record that we've seen them for anouncement purposes.
                self.factory.peer.peer_seen(self.remote_address[0], 
                    self.remote_address[1], int(time.time()))
            
        except:
            print "Exception processing command: {}".format(parts)
            traceback.print_exc()
            
            # Disconnect from people who send us garbage
            self.disconnect()
        
    def lineReceived(self, data):
        """
        We got a command from the remote peer. Handle it.
        
        TODO: Enforce that any of these happen in the correct order.
        
        """
        
        # Split the command into parts on spaces.
        parts = [part.strip() for part in data.split()]
        
        # Handle it in its own thread. This is the only other thread that ever
        # runs.
        reactor.callInThread(self.handle_message, parts)
            
class ServerFactory(protocol.ServerFactory):
    """
    This is a Twisted server factory, responsible for taking incoming
    connections and starting Servers to serve them. It is part of a Peer.
    
    """
    
    def __init__(self, peer):
        """
        Make a new ServerFactory with a reference to the Peer it is handling
        incoming connections for.
        
        """
        
        # Keep the peer around
        self.peer = peer
        
    def buildProtocol(self, addr):
        """
        Make a new server protocol. It's talking to the given
        address.
        
        """
        
        print "Server got connection from ", addr
        
        # Make a new BlockchainProtocol that knows we are its factory. It will
        # then talk to our peer.
        return BlockchainProtocol(self, (addr.host, addr.port), incoming=True)
        
class ClientFactory(protocol.ClientFactory):
    """
    This is a Twisted client factory, responsible for making outgoing
    connections and starting Clients to run them. It is part of a Peer.
    
    """
    
    def __init__(self, peer):
        """
        Make a new ClientFactory with a reference to the Peer it is producing
        outgoing connections for.
        
        """
        
        # Keep the peer around
        self.peer = peer
        
    def buildProtocol(self, addr):
        """
        Make a new client protocol. It's going to be connecting to the given
        address.
        
        """
        
        print "Client made connection to ", addr
        
        # Make a new BlockchainProtocol that knows we are its factory. It will
        # then talk to our peer.
        return BlockchainProtocol(self, (addr.host, addr.port))
        
    def clientConnectionLost(self, connector, reason):
        """
        We've lost a connection we made.
        
        """
        
        # Record that the outgoing connection is gone
        self.peer.lost_outgoing_connection(connector.getDestination().host)
        
        print "Lost outgoing connection.  Reason:", reason

    def clientConnectionFailed(self, connector, reason):
        """
        We failed to make an outgoing connection.
        
        """
        
        # Record that the outgoing connection is gone
        self.peer.lost_outgoing_connection(connector.getDestination().host)
        
        print "Outgoing connection failed. Reason:", reason
            
class Peer(object):
    """
    Represents a peer in the p2p blockchain network. Implements a protocol bsed
    on the Bitcoin p2p protocol. Keeps a Blockchain of valid blocks, and handles
    downloading new blocks and broadcasting new blocks to peers.
    """
    
    def __init__(self, network, version, blockchain, port=8007, 
        optimal_connections=10, tick_period=60, peer_timeout = 60 * 60 * 12):
        """
        Make a new Peer in the given network (identified by a string), with the
        given version integer, that keeps its blocks in the given Blockchain.
        Will only connect to other peers in the same network with the same
        version integer.
        
        network must be a printable string with no spaces or newlines.
        
        version must be an integer.
        
        port gives a port to listen on. If none is specified, a default
        port is used.
        
        optimal_connections is the number of connections we want to have. We
        will periodically try to get new connections or drop old ones.
        
        tick_period is how often to tick and ping our peers/broadcast our
        address/try to make new connections/drop extra connections, in seconds.
        
        peer_timeout is how long to remember nodes sicne we last heard from
        them.
        
        The caller needs to run the Twisted reactor before this does anything.
        This can be doine through run().
        
        """
        
        # Remember our network name and version number
        self.network = network
        self.version = version
        
        # Save the blockchain
        self.blockchain = blockchain
        
        # Remember our port. We may need to tell people about it if we connect
        # to them.
        self.port = port
        
        # Remember our optimal number of connections
        self.optimal_connections = optimal_connections
        
        # Remember our peer remembering timeout
        self.peer_timeout = peer_timeout
        
        # Make an endpoint to listen on
        self.endpoint = endpoints.TCP4ServerEndpoint(reactor, port)
        
        # Make a Twisted ServerFactory
        self.server = ServerFactory(self)
        
        # Listen with it
        self.endpoint.listen(self.server)
        
        # Make a Twisted ClientFactory to make outgoing connections
        self.client = ClientFactory(self)
        
        # Keep a dictionary of known peers: from host to (port, last-seen)
        # tuples, as in BitMessage
        self.known_peers = {}
        
        # Keep a set of hostnames we have open, outgoing connections to
        self.outgoing_hosts = set()
        
        # Keep a set of open connections (Protocol objects)
        self.connections = set()
        
        # Remember our tick frequency
        self.tick_period = tick_period
        # And schedule a tick right away.
        reactor.callLater(0, self.tick)
        
        # Make a lock so this whole thing can basically be a monitor
        self.lock = threading.RLock()
        
        # Remember if we need to repoll our peers for blocks
        self.repoll = False
        
    def connect(self, host, port):
        """
        Make a new connection to the given host and port, as a client.
        
        """
        
        with self.lock:
            # Remember that we are connecting to this host
            self.outgoing_hosts.add(host)
            
            print "Connecting to {} port {}".format(host, port)
            
            # Queue making a connection with our ClientFactory in the Twisted
            # reactor.
            reactor.connectTCP(host, port, self.client)
    
    
    def made_connection(self, connection):
        """
        Called when a connection is made. Add the connection to the set of
        connections.
        
        """
        
        with self.lock:
            # Add the connection to our list of connections
            self.connections.add(connection)
        
    def lost_connection(self, connection):
        """
        Called when a connection is closed (either normally or abnormally).
        Remove the connection from our set of connections.
        
        """
        
        with self.lock:
            # Drop the connection from our list of connections
            self.connections.discard(connection)
        
    
    def lost_outgoing_connection(self, host):
        """
        Called when an outgoing connection is lost or fails.
        Removes that hostname from the list of open outgoing connections.
        
        """
        
        with self.lock:
            # No longer connecting to this host
            self.outgoing_hosts.discard(host)
    
    def get_peers(self):
        """
        Return a list of (host, port, time seen) tuples for all peers we know
        of.
        
        """
        
        with self.lock:
            return [(host, host_data[0], host_data[1]) for host, host_data in 
                self.known_peers.iteritems()]
            
    def peer_seen(self, host, port, time_seen):
        """
        Another peer has informed us of the existence of this peer. Remember it,
        and broadcast to to our peers.
        
        """
        
        with self.lock:
        
            if self.known_peers.has_key(host):
                # We know of this peer, but we perhaps ought to update the last
                # heard from time
                
                # Get the port we know for that host, and the time we last saw
                # them
                known_port, our_time_seen = self.known_peers[host]
                
                if time_seen > our_time_seen and time_seen <= time.time():
                    # They heard from them more recently, but not in the future.
                    # Update our time last seen.
                    self.known_peers[host] = (known_port, time_seen)
            else:
                # This is a new peer.
                # Save it.
                self.known_peers[host] = (port, time_seen)
                
                # Broadcast it
                for connection in self.connections:
                    connection.send_message(["ADDR", host, port, time_seen])
    
    def set_repoll(self):
        # We saw an unverifiable block. We may be out of date.
        # Next time we tick, do a getblocks to all our peers.
        
        # Too simple to need to lock
        self.repoll = True
                
    def tick(self):
        """
        See if we have the optimal number of outgoing connections. If we have
        too few, add some.
        
        TODO: Broadcast our address.
        
        """
        
        with self.lock:
        
            # How many connections do we have right now?
            current_connections = len(self.connections)
            print "Tick from localhost port {}: {} of {} connections".format(
                self.port, current_connections, self.optimal_connections)
            
            for connection in self.connections:
                print "\tTo {} port {}".format(*connection.remote_address)
            
            print "Blockchain height: {}".format(
                len(self.blockchain.hashes_by_height))
            # -3 is a hack because we have non-blocks in there.
            print "Blocks known: {}".format(
                len(self.blockchain.blockstore) - 3) 
            print "Blocks pending: {}".format(
                len(self.blockchain.pending_callbacks))
            print "Transactions pending: {}".format(len(
                self.blockchain.transactions))
            
            if (len(self.outgoing_hosts) < self.optimal_connections and 
                len(self.known_peers) > 0):
                # We don't have enough outgoing connections, but we do know some
                # peers.
                
                # Find a peer we aren't connected to and connect to them
                host = random.sample(self.known_peers, 1)[0]
                
                # Try at most 100 times to find a host we aren't connected to
                attempt = 1
                while host in self.outgoing_hosts and attempt < 100:
                    # Try a new host
                    host = random.sample(self.known_peers, 1)[0]
                    
                    # Increment attempt
                    attempt += 1
                    
                # TODO: This always makes two attempts at least
                    
                if attempt < 100:
                    # We found one!
                    # Connect to it.
                    
                    # Get the port (and discard the last heard from time)
                    port, _ = self.known_peers[host]
                
                    # Connect to it.
                    self.connect(host, port)
                    
            # Throw out peers that are too old. First compile a list of their
            # hostnames.
            too_old = []

            for host, (port, last_seen) in self.known_peers.iteritems():
                if time.time() - last_seen > self.peer_timeout:
                    # We haven't heard from/about this node recently enough.
                    too_old.append(host)
                    
            # Now drop all the too old hosts
            for host in too_old:
                del self.known_peers[host]
                
            # Broadcast all our hosts.
            print "{} known peers:".format(len(self.known_peers))
            for host, (port, last_seen) in self.known_peers.iteritems():
                print "\tPeer {} port {} last seen {}".format(host, port, 
                    time2string(last_seen))
                for connection in self.connections:
                    connection.send_message(["ADDR", host, port, last_seen])
            
            # Do we need to re-poll for blocks?
            if self.repoll:
                self.repoll = False
                print "Repolling due to unverifiable block."
                
                # Compose just one message
                message = (["GETBLOCKS"] + 
                    [bytes2string(block_hash) for block_hash in 
                    self.blockchain.get_block_locator()])
                
                for connection in self.connections:
                    connection.send_message(message) 
                        
            # Tick again later
            reactor.callLater(self.tick_period, self.tick)
        
            print "Tick complete."
        
    def announce_block(self, block_hash):
        """
        Tell all of our connected peers about a block we have.
        """
        
        with self.lock:
            for connection in self.connections:
                # Send an INV message with the hash of the thing we have, in
                # case they want it.
                connection.send_message(["INV", bytes2string(block_hash)])
                
    def announce_transaction(self, transaction_hash):
        """
        Tell all of our connected peers about a transaction we have.
        """
        
        with self.lock:
            for connection in self.connections:
                # Send a TXINV message with the hash of the thing we have, in
                # case they want it.
                connection.send_message(["TXINV", bytes2string(
                    transaction_hash)])
            
    def was_block_valid(self, block_hash, status):
        """
        Called when a block we received becomes verifiable. Takes the block
        hash and a status of True if the block was valid, or False if it
        wasn't.
        
        """
        
        if status:
            # Tell all our peers about this awesome new block
            self.announce_block(block_hash)
        else:
            # Re-poll for blocks when we get a chance. Maybe it was too far in
            # the future or something.
            self.set_repoll()
    
    
    def was_transaction_valid(self, transaction_hash, status):
        """
        Called when a transaction is verified and added to the Blockchain's
        collection of transactions (i.e. those which one might want to include
        in a block), or rejected. Status is True for valid transactions, and
        false for invalid ones.
        
        Broadcasts transactions which are valid.
        """
        
        if status:
            # The transaction was valid. Broadcast it.
            self.announce_transaction(transaction_hash)
    
    
    def send_block(self, block):
        """
        Given a new block, will add it to our blockchain and send it on its way
        to all peers, if appropriate.
        
        """
        
        # Queue the block, and, if valid, announce it
        self.blockchain.queue_block(block, 
            callback=self.was_block_valid)
            
    def send_transaction(self, transaction):
        """ 
        Given a transaction bytestring, will put it in our queue of transactions
        and send it off to our peers, if appropriate.
        
        """
        
        # Add the transaction, and, if valid, announce it
        self.blockchain.add_transaction(transaction, 
            callback=self.was_transaction_valid)
        
    def run(self):
        """
        Run the Twisted reactor and actually make this peer do stuff. Never
        returns.
        
        Exists so people using our module don't need to touch Twisted directly.
        They can just do their own IPC and keep us in a separate process.
        
        """
        
        reactor.run()
