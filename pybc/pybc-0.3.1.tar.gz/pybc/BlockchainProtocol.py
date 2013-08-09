"""
BlockchainProtocol.py: contains the BlockchainProtocol class.

"""


import time, traceback, collections
from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver

from pybc.Block import Block
from pybc.util import string2bytes, bytes2string

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
        
        incoming specifies whether this connection is incoming or not. If it's
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
        
        # Keep a queue of block hashes to download. Don't get too many at once.
        self.queue = collections.deque()
        
        # Keep a set of things in th queue.
        self.queued = set()
        
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
                
        # Make sure to process the queue periodically
        reactor.callLater(1, self.process_queue)
    
    def connectionLost(self, reason):        
        """
        This connection has been lost.
        """
        
        # We're no longer a connection that the peer should send things to.
        self.factory.peer.lost_connection(self)
        
        print "Protocol lost connection. Reason: ", reason
        
        # Drop our download queue so we don't stick around trying to download
        # it.
        self.queue.clear()
        self.queued.clear()
    
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
                # This is a network command, telling us the network and version
                # of the remote host. If we like them (i.e. they are equal to
                # ours), send back an acknowledgement with our network info.
                # Also start requesting peers and blocks from them.
                
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
                
                if (not self.factory.peer.blockchain.has_block(block_hash) and 
                    block_hash not in self.queued):
                    
                    # We need this block!
                    self.queue.append(block_hash)
                    self.queued.add(block_hash)
                    
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
        
    def process_queue(self):
        """
        Download a block from the queue.
        """
        
        for _ in xrange(100):
            # Only ask for 100 blocks at a time.
            if len(self.queue) > 0:
                # Get the bytestring hash of the next block to ask for
                block_hash = self.queue.popleft()
                self.queued.remove(block_hash)
                
                if not self.factory.peer.blockchain.has_block(block_hash):
                    # We still need it. Go ask for it.
                    self.send_message(["GETDATA", bytes2string(block_hash)])
                
        # Process the queue again.
        reactor.callLater(1, self.process_queue)
