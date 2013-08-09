"""
Peer.py: contains the Peer class.

"""

import random, time, threading

from twisted.internet import reactor, endpoints

from pybc.ClientFactory import ClientFactory
from pybc.ServerFactory import ServerFactory
from pybc.util import time2string, bytes2string

import sqliteshelf

class Peer(object):
    """
    Represents a peer in the p2p blockchain network. Implements a protocol bsed
    on the Bitcoin p2p protocol. Keeps a Blockchain of valid blocks, and handles
    downloading new blocks and broadcasting new blocks to peers.
    """
    
    def __init__(self, network, version, blockchain, peer_file = ":memory:", 
        external_address=None, port=8007, optimal_connections=10, 
        tick_period=60, peer_timeout = 60 * 60 * 12):
        """
        Make a new Peer in the given network (identified by a string), with the
        given version integer, that keeps its blocks in the given Blockchain.
        Will only connect to other peers in the same network with the same
        version integer.
        
        network must be a printable string with no spaces or newlines.
        
        version must be an integer.
        
        peer_file gives a filename to store a persistent peer database in. It
        defaults to ":memory:", which keeps the database in memory where it
        isn't really persistent.
        
        external_address, if specified, gives an address or hostname at which we
        can announce our presence on every tick.
        
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
        
        # Remember our external address (which may be None)
        self.external_address = external_address
        
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
        
        # Keep an sqliteshelf of known peers: from host to (port, last-seen)
        # tuples, as in BitMessage.
        self.known_peers = sqliteshelf.SQLiteShelf(peer_file, table="peers", 
            lazy=True)
        
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
            
            print "{} outgoing connections:".format(len(self.outgoing_hosts))
            for host in self.outgoing_hosts:
                print "\t To {}".format(host)
            
            print "Blockchain height: {}".format(
                len(self.blockchain.hashes_by_height))
            print "Blocks known: {}".format(
                self.blockchain.get_block_count())
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
            
            if self.external_address is not None:
                # Broadcast ourselves, since we know our address.
                for connection in self.connections:
                    connection.send_message(["ADDR", self.external_address, 
                        self.port, int(time.time())])
            
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
            
            # Sync the blockchain to disk.
            self.blockchain.sync()
            
            # Sync the known peers to disk
            self.known_peers.sync()
                        
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
