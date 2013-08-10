"""
Blockchain.py: ontains the Blockchain class.

"""

import hashlib, struct, time, threading, collections

from pybc.Block import Block
from pybc.State import State
import pybc.util
import sqliteshelf


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
        may get an extension appended to it) and an initial State object to use
        if none can be loaded from the file, construct a Blockchain.
        
        """
        
        # Set up our retargeting logic. We retarget so that it takes
        # retarget_time to generate retarget_period blocks. This specifies a 1
        # minute blocktime.
        self.retarget_time = 600
        self.retarget_period = 10
        
        # Keep the PowAlgorithm around
        self.algorithm = algorithm
        
        # Keep a database of all blocks by block hash.
        self.blockstore = sqliteshelf.SQLiteShelf(store_filename, 
            table="blocks", lazy=True)
        
        # Keep a database for longest-fork data (really a table in the same
        # database; sqlite3 makes multiple accesses to the same database OK)
        self.fork_data = sqliteshelf.SQLiteShelf(store_filename, 
            table="fork", lazy=True)
        
        # Keep the highest Block around, so we can easily get the top of the
        # highest fork.
        self.highest_block = None
        
        # We keep the highest block's hash in the fork database under "highest"
        if self.fork_data.has_key("highest"):
            self.highest_block = self.blockstore[self.fork_data["highest"]]
        
        # Keep a list of block hashes by height in our current fork, for
        # efficient access by height.
        self.hashes_by_height = []
        
        # We keep that in the fork data too
        if self.fork_data.has_key("hashes_by_height"):
            self.hashes_by_height = self.fork_data["hashes_by_height"]
            
        # We need a lock so we can be a monitor and thus thread-safe
        self.lock = threading.RLock()
        
        # This is a dict of lists of pending blocks by the hash we need to
        # verify them, and then by their own hash (to detect duplicates)
        self.pending_on = collections.defaultdict(dict)
        
        # This is a dict of callbacks by pending block hash
        self.pending_callbacks = {}
        
        # This holds our pending transactions as bytestrings by hash.
        self.transactions = {}
        
        # This keeps the State at the tip of the longest fork. If we don't find
        # a saved State, use the one provided. Its type determines the methods
        # we use to maintain state.
        self.state = initial_state
        if self.fork_data.has_key("state"):
            # Load the saved State.
            self.state = self.fork_data["state"]
            
        # We keep a cache of states after blocks, by block hash
        self.state_cache = collections.OrderedDict()
        
        # How big should the cache be?
        self.state_cache_limit = 10

    def has_block(self, block_hash):
        """
        Return True if we have the given block, and False otherwise.
        
        """
        
        with self.lock:
            # Lock since sqliteshelf isn't thread safe
            return self.blockstore.has_key(block_hash)

    def get_block(self, block_hash):
        """
        Return the block with the given hash. Raises an error if we don't have
        it.
        
        """
        
        with self.lock:
            # Lock since sqliteshelf isn't thread safe
            return self.blockstore[block_hash]


    def get_block_count(self):
        """
        Return the number of blocks we know about (not just the number in the
        longest chain).
        
        """
        
        return len(self.blockstore)

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
        
        with self.lock:
            # We're going to touch our databases, so we have to lock.
        
        
            if next_block.height == 0:
                # It's a genesis block. We can always check those.
                return True
            
            # The block store never contains any blocks we can't verify, so if
            # we have the parent, we can verify this block.
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
                    pybc.util.time2string(next_block.timestamp), 
                    pybc.util.time2string(now))
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
                    pybc.util.bytes2hex(self.next_block_target(previous_block)))
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
        
        # Lock since we use the blockstore
        with self.lock:
        
            if previous_block is None:
                # No blocks yet, so this is the starting target. You get a 0 bit
                # as the first bit instead of a 1 bit every other hash. So to
                # get n leading 0 bits takes on average 2^n hashes. n leading
                # hex 0s takes on average 16^n hashes.
                return struct.pack(">Q", 0x00000fffffffffff) + "\xff" * 56
            else:
                # Easy default behavior: re-target every 10 blocks to a rate of
                # 10 block per minute, but don't change target by more than
                # 4x/0.25x
                
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
                        
                    # At constant hashrate, the generation rate scales linearly
                    # with the target. So if we took a factor of x too long,
                    # increasing the target by a factor of x should help with
                    # that.
                    factor = float(time_taken) / ideal_time
                    
                    print "Want to scale generation rate by {}".format(factor)
                    
                    # Don't scale too sharply.
                    if factor > 4:
                        factor = 4
                    if factor < 0.25:
                        factor = 0.25
                    
                    print "Will actually scale by: {}".format(factor)
                    
                    # Load the target as a big int
                    old_target = pybc.util.bytes2long(previous_block.target)
                    
                    print "{} was old target".format(pybc.util.bytes2hex(
                        previous_block.target))
                    
                    # Multiply it
                    new_target = long(old_target * factor)
                    
                    print "new / old = {}".format(new_target / old_target)
                    print "old / new = {}".format(old_target / new_target)
                    
                    new_target_bytes = pybc.util.long2bytes(new_target)
                    
                    while len(new_target_bytes) < 64:
                        # Padd to the appropriate length with nulls
                        new_target_bytes = "\0" + new_target_bytes
                    if len(new_target_bytes) > 64:
                        # New target would be too long. Don't change
                        print "No change because new target is too long."
                        return previous_block.target
                    
                    print "{} is new target".format(pybc.util.bytes2hex(
                        new_target_bytes))
                        
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
        on the new fork, and that these changes are sent to the fork database.
        
        Also, change our State and send that to the fork database.
        
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
            # Put the new State in the fork database.
            self.fork_data["state"] = self.state
        
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
                    
            # Save our hashes by height changes to the fork database.
            self.fork_data["hashes_by_height"] = self.hashes_by_height
    
    def queue_block(self, next_block, callback=None):
        """
        We got a block that we think goes in the chain, but we may not have all
        the previous blocks that we need to verify it yet.
        
        Put the block into a receiving queue.
        
        If the block is eventually verifiable, call the callback with the hash
        and True if it's good, or the hash and False if it's bad.
        
        If the same block is queued multiple times, and it isn't immediately
        verifiable, only the last callback for the block will be called.
        
        """
        
        # This holds all the callbacks we need to call, so we can call them
        # while we're not holding the lock. It's a list of function, argument
        # tuple tuples.
        to_call = []
        
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
                        # Later, call the callback.
                        to_call.append((callback, (next_block.block_hash(),
                            True)))
                    
                    print "Block height {} immediately verified: {}".format(
                        next_block.height,
                        pybc.util.bytes2string(next_block.block_hash()))
                    
                    # Record that we added the block
                    added_hashes.append(next_block.block_hash())
                else:
                    print "Invalid block:\n{}".format(next_block)
                    if callback is not None:
                        # Later, call the callback.
                        to_call.append((callback, (next_block.block_hash(),
                            False)))
            else:
                # Add this block to the pending blocks for its parent. If it's
                # already there, we just replace it
                self.pending_on[next_block.previous_hash][
                    next_block.block_hash()] = next_block
                # Remember the callback for this block, which chould be called
                # when it is verified.
                self.pending_callbacks[next_block.block_hash()] = callback
                
                print "Block height {}, hash {} pending on parent {}".format(
                        next_block.height,
                        pybc.util.bytes2string(next_block.block_hash()), 
                        pybc.util.bytes2string(next_block.previous_hash))
            
            while len(added_hashes) > 0:
                # There are blocks that we have added, but we haven't checked
                # for other blocks pending on them. Do that.
                
                # Pop off a hash to check
                hash_added = added_hashes.pop()
                # Get the dict of waiters by waiter hash
                waiters = self.pending_on[hash_added]
                
                # Remove it
                del self.pending_on[hash_added]
                
                print "{} waiters were waiting on {}".format(len(waiters), 
                    pybc.util.bytes2string(hash_added))
                    
                for waiter_hash, waiter in waiters.iteritems():
                    # We ought to be able to verify and add each waiter.
                    
                    # Get the callback
                    waiter_callback = self.pending_callbacks[waiter_hash]
                    
                    # Remove it from the collection of remaining callbacks
                    del self.pending_callbacks[waiter_hash]
                
                    if self.can_verify_block(waiter):
                        # We can verify the block right now (ought to always be
                        # true)
                        if self.verify_block(waiter):
                            # The block is good! Add it
                            self.add_block(waiter)
                            
                            if waiter_callback is not None:
                                # Call the callback later
                                to_call.append((waiter_callback, 
                                    (waiter_hash, True)))
                            
                            print "Queued block height {} verified: {}".format(
                                waiter.height,
                                pybc.util.bytes2string(waiter_hash))
                            
                            # Record that we added the pending block, so things
                            # pending on it can now be added
                            added_hashes.append(waiter_hash)
                        else:
                            # TODO: throw out blocks waiting on invalid blocks.
                            # If we have any of those, there's probablt a hard
                            # fork.
                            
                            print "Queued block invalid: {}".format(
                                pybc.util.bytes2string(waiter_hash))
                            
                            if waiter_callback is not None:
                                # Call the callback later
                                to_call.append((waiter_callback, (waiter_hash, 
                                    False)))
                    else:
                        # This should never happen
                        print("Couldn't verify a waiting block when its parent "
                            "came in!")
                            
        # Now we're out of the locked section.
        print "Dispatching {} block validity callbacks.".format(len(to_call))
        for callback, args in to_call:
            # Call all the callbacks, in case they need to get a lock that
            # another thread has and that thread is waiting on this thread.
            callback(*args)
    
    def cache_state(self, block_hash, state):
        """
        Put this State object in the state cache as the state after the block
        with the given hash. Make it the most recently used state, and eject
        older states if needed to make this state fit.
        
        """
    
        if self.state_cache.has_key(block_hash):
            # Take it out so we can move it to the end.
            del self.state_cache[block_hash]
        elif len(self.state_cache) == self.state_cache_limit:
            # Pop the oldes thing because it's full
            self.state_cache.popitem()
        
        # Add the entry
        self.state_cache[block_hash] = state
            
    
    def state_after(self, block):
        """
        Given that our State is currently up to date with our current
        highest_block, return a State that is in effect after the given block.
        
        block may be None.
        
        Walks the blockchain from the tip of the highest fork to the given
        block, which must be in the block store.
        
        Because that's probably what's responsible for poor performance when
        trying to fork, we keep an LRU cache of states.
        
        TODO: can we do real pathfinding?
        
        """
        
        with self.lock:
        
            # What's the hash of the block?
            if block is not None:
                block_hash = block.block_hash()
            else:
                block_hash = "\0" * 64
            
            if self.state_cache.has_key(block_hash):
                print "Getting cached state"
                # We already have the answer. Get it from the cache.
                state = self.state_cache[block_hash]
                
                # Mark the state used 
                self.cache_state(block_hash, state)
                
                # Return it
                return state
        
            if block == self.highest_block:
                print "Using current state."
                # We already have the state after this
                self.cache_state(block_hash, self.state)
                return self.state
        
            if self.highest_block is None:
                print "Making genisis state"
                # Easy case: this must be a genesis block.
                # Use the current (empty) state updated with the new block
                state = self.state.step_forwards(block)
                self.cache_state(block_hash, state)
                return state
                
            if (block is not None and 
                self.state_cache.has_key(block.previous_hash)):
                print "Using parent state"
                # Special case: we have the state after the block before this
                # block, so we can just add this block on top.
                # TODO: real states and pathfinding
                state = self.state_cache[block.previous_hash]
                
                # Mark the state used 
                self.cache_state(block.previous_hash, state)
                
                # Advance the State
                state = state.step_forwards(block)
                
                # Cache and return it
                self.cache_state(block_hash, state)
                return state
            
            print "Walking blockchain for state"
            # If we get here, we know we have a highest block, and that we need
            # to walk from there to the block we're being asked about.
            
            # How many blocks did we walk?
            blocks_walked = 0
            
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
                blocks_walked += 1
                
            # Now we've reverted to the post-common-ancestor state. TODO: Can't
            # we just get a known state here? Or can we save a state per tip?
            
            # Now apply all the blocks from there to block in forwards order.
            # First get a list of them
            blocks_to_apply = []
            
            if block is None:
                # We want the state before any blocks, so start at no blocks and
                # go back to the common ancestor (which also ought to be no
                # blocks).
                position = "\0" * 64
            else:
                # We want the state after a given block, so we have to grab all
                # the blocks between it and the common ancestor, and then run
                # them forwards.
                position = block.block_hash()
                
            while position != ancestor_hash:
                # For each block back to the common ancestor... (We know we
                # won't go off the start of the blockchain, since ancestor is
                # known to actually be a common ancestor hash.)
            
                # Collect the blocks on the path from block to the common
                # ancestor.
                blocks_to_apply.append(self.blockstore[position])
                
                # Step back a block
                position = self.blockstore[position].previous_hash
                blocks_walked += 1
                
            # Flip the blocks that need to be applied into chronological order.
            blocks_to_apply.reverse()
            
            for block_to_apply in blocks_to_apply:
                # Apply the block to the state
                state = state.step_forwards(block_to_apply)
            
            print "Walked {} blocks".format(blocks_walked)
            
            # We've now updated to the state for after the given block.
            self.cache_state(block_hash, state)
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
                        # And save that back to the fork database
                        self.fork_data["hashes_by_height"] = \
                            self.hashes_by_height
                            
                        # Update the State with a simple step
                        self.state = self.state.step_forwards(next_block)
                        # And save that back to the fork database too
                        self.fork_data["state"] = self.state
                            
                    # Set the highest block to the new block.
                    self.highest_block = next_block
                    
                    # Put the new highest block's hash into the fork database
                    # "under highest".
                    self.fork_data["highest"] = self.highest_block.block_hash()
            
                    # Now there is a new block on the longest chain. Throw out
                    # all transactions that are now invalid on top of it. First,
                    # make a list of them.
                    
                    # Note: Expect some console spam when debugging invalid
                    # transactions, which are only really expected here.
                    invalid_transaction_hashes = [hash for hash, transaction in 
                        self.transactions.iteritems() if not 
                        self.verify_transaction(transaction, 
                        self.highest_block)]
                        
                    # Then, remove them all
                    for transaction_hash in invalid_transaction_hashes:
                        del self.transactions[transaction_hash]
                        
                    print "Dropped {} invalid queued transactions".format(len(
                        invalid_transaction_hashes))
                
            else:
                # Block we tried to add failed verification. Complain.
                raise Exception("Invalid block!")
    
    def sync(self):
        """
        Save all changes to the blockstore to disk. Since the blockstore is
        always in a consistent internal state when none of its methods are
        executing, just call this periodically. to make sure things get saved.
        
        """
        
        with self.lock:
            # Save the actual blocks
            self.blockstore.sync()
            # Save the metadata about what fork we're on, which depends on
            # blocks. It can be incorrect if the blocks get saved and it
            # doesn't, but not invalid.
            self.fork_data.sync()
            
            
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
        
        # No need to lock. This is atomic and hits against an in-memory dict
        # rather than a persistent one.
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
                
                # Record that it was verified
                verified = True
            
            else:
                # Record that it wasn't verified.
                verified = False
                
        # Notify the callback outside the critical section.
        if callback is not None:
            callback(transaction_hash, verified)
