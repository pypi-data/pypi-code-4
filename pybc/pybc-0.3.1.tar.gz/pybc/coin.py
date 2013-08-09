#!/usr/bin/env python2.7
# coin.py: a coin implemented on top of pybc

import struct, hashlib, traceback, time, threading
import pybc, pyelliptic
import sqliteshelf

class Transaction(object):
    """
    Represents a transaction on the blockchain. 
    
    A transaction is a list of inputs (represented by transaction hash, output
    index), a list of outputs (represented by amounts and destination public key
    hash), and a list of authorizations (public key, signature) signing the
    previous two lists. It also has a timestamp, so that two generation
    transactions to the same destination address won't have the same hash. (If
    you send two block rewards to the same address, make sure to use different
    timestamps!)
    
    Everything except public keys are hashed sha512 (64 bytes). Public keys are
    hashed sha256 (32 bytes).
    
    A transaction is properly authorized if all of the inputs referred to have
    destination hashes that match public keys that signed the transaction.
    
    A generation transaction (or fee collection transaction) is a transaction
    with no inputs. It thus requires no authorizations.
    
    Any input not sent to an output is used as a transaction fee, and added to
    the block reward.
    
    Has a to_bytes and a from_bytes like Blocks do.
    
    """
    
    def __init__(self):
        """
        Make a new Transaction with no inputs or outputs.
        
        """
        
        # Set the timestamp to the transaction's creation time (i.e. now).
        # Nobody actually verifies it, so it's really 8 arbitrary bytes.
        self.timestamp = int(time.time())
        
        # Make a list of input tuples (transaction hash, output index).
        self.inputs = []
        
        # Make a list of output tuples (amount, destination public key hash)
        self.outputs = []
        
        # Make a list of authorization tuples (public key, signature of inputs
        # and outputs)
        self.authorizations = []
        
    def __str__(self):
        """
        Represent this transaction as a string.
        
        """
        
        # These are the lines we will return
        lines = []
        
        lines.append("---Transaction {}---".format(pybc.time2string(
            self.timestamp)))
        lines.append("{} inputs".format(len(self.inputs)))
        for transaction, index, amount, destination in self.inputs:
            # Put every input (another transaction's output)
            lines.append("\t{} addressed to {} from output {} of {}".format(
                amount, pybc.bytes2string(destination), index, 
                pybc.bytes2string(transaction)))
        lines.append("{} outputs".format(len(self.outputs)))
        for amount, destination in self.outputs:
            # Put every output (an amount and destination public key hash)
            lines.append("\t{} to {}".format(amount, 
                pybc.bytes2string(destination)))
        lines.append("{} authorizations".format(len(self.authorizations)))
        for public_key, signature in self.authorizations:
            # Put every authorizing key and signature.
            lines.append("\tKey: {}".format(pybc.bytes2string(public_key)))
            lines.append("\tSignature: {}".format(
                pybc.bytes2string(signature)))
                
        # Put the hash that other transactions use to talk about this one        
        lines.append("Hash: {}".format(pybc.bytes2string(
            self.transaction_hash())))
            
        return "\n".join(lines)
        
    def transaction_hash(self):
        """
        Return the SHA512 hash of this transaction, by which other transactions
        may refer to it.
        
        """
        
        return hashlib.sha512(self.to_bytes()).digest()
        
    def add_input(self, transaction_hash, output_index, amount, destination):
        """
        Take the coins from the given output of the given transaction as input
        for this transaction. It is necessary to specify and store the amount
        and destination public key hash of the output, so that the blockchain
        can be efficiently read backwards.
        
        """
        
        self.inputs.append((transaction_hash, output_index, amount, 
            destination))
        
    def add_output(self, amount, destination):
        """
        Send the given amount of coins to the public key with the given hash.
        
        """
        
        self.outputs.append((amount, destination))
        
    def add_authorization(self, public_key, signature):
        """
        Add an authorization to this transaction by the given public key. The
        given signature is that key's signature of the transaction header data
        (inputs and outputs).
        
        Both public key and signature must be bytestrings.
        
        """
        
        self.authorizations.append((public_key, signature))
    
    def get_leftover(self):
        """
        Return the sum of all inputs minus the sum of all outputs.
        """
        
        # This is where we store our total
        leftover = 0    
    
        for _, _, amount, _ in self.inputs:
            # Add all the inputs on the + side
            leftover += amount
            
        for amount, _ in self.outputs:
            # Add all the outputs on the - side
            leftover -= amount
            
        return leftover
    
    def verify_authorizations(self):
        """
        Returns True if, for every public key hash in the transaction's inputs,
        there is a valid authorization signature of this transaction by a public
        key with that hash.
        
        """
    
        # Get the bytestring that verifications need to sign
        message_to_sign = self.header_bytes()
    
        # This holds SHA256 hashes of all the pubkeys with valid signatures
        valid_signers = set()
    
        for public_key, signature in self.authorizations:
            # Check if each authorization is valid.
            if pyelliptic.ECC(pubkey=public_key).verify(signature, 
                message_to_sign):
                
                # The signature is valid. Remember the public key hash.
                valid_signers.add(hashlib.sha256(public_key).digest())
                
            else:
                print "Invalid signature!"
                # We're going to ignore extra invalid signatures on
                # transactions. What could go wrong?
            
        for _, _, _, destination in self.inputs:
            if destination not in valid_signers:
                # This input was not properly unlocked.
                return False
                
        # If we get here, all inputs were to destination pubkey hashes that has
        # authorizing signatures attached.
        return True
    
    def pack_inputs(self):
        """
        Return the inputs as a bytestring.
        
        """
        
        # Return the 4-byte number of inputs, followed by a 64-byte transaction
        # hash, a 4-byte output index, an 8 byte amount, and a 32 byte
        # destination public key hash for each input.
        return struct.pack(">I", len(self.inputs)) + "".join(
            struct.pack(">64sIQ32s", *source) for source in self.inputs)
            
    def unpack_inputs(self, bytestring):
        """
        Set this transaction's inputs to those encoded by the given bytestring.
        
        """
        
        # Start with a fresh list of inputs.
        self.inputs = []
        
        # How many inputs are there?
        (input_count,) = struct.unpack(">I", bytestring[0:4])
        
        # Where are we in the string
        index = 4
        
        for _ in xrange(input_count):
            # Unpack that many 108-byte records of 64-byte transaction hashes,
            # 4-byte output indices, 8-byte amounts, and 32-byte destination
            # public key hashes.
            self.inputs.append(struct.unpack(">64sIQ32s",
                bytestring[index:index + 108]))
            index += 108
            
    def pack_outputs(self):
        """
        Return the outputs as a bytestring.
        
        """
        
        # Return the 4-byte number of outputs, followed by an 8-byte amount and
        # a 32-byte destination public key hash for each output
        return struct.pack(">I", len(self.outputs)) + "".join(
            struct.pack(">Q32s", *destination) for destination in self.outputs)
            
    def unpack_outputs(self, bytestring):
        """
        Set this transaction's outputs to those encoded by the given bytestring.
        
        """
        
        # Start with a fresh list of outputs.
        self.outputs = []
        
        # How many outputs are there?
        (output_count,) = struct.unpack(">I", bytestring[0:4])
        
        # Where are we in the string
        index = 4
        
        for _ in xrange(output_count):
            # Unpack that many 40-byte records of 8-byte amounts and 32-byte
            # destination public key hashes.
            self.outputs.append(struct.unpack(">Q32s", 
                bytestring[index:index + 40]))
            index += 40
            
    def pack_authorizations(self):
        """
        Return a bytestring of all the authorizations for this transaction.
        
        """
        
        # We have a 4-byte number of authorization records, and then pairs of 4
        # -byte-length and n-byte-data strings for each record.
        
        # This holds all our length-delimited bytestrings as we make them
        authorization_bytestrings = []
        
        for public_key, signature in self.authorizations:
            # Add the public key
            authorization_bytestrings.append(struct.pack(">I", 
                len(public_key)) + public_key)
            # Add the signature
            authorization_bytestrings.append(struct.pack(">I", 
                len(signature)) + signature)
        
        # Send back the number of records and all the records.
        return (struct.pack(">I", len(self.authorizations)) +
            "".join(authorization_bytestrings))
            
    def unpack_authorizations(self, bytestring):
        """
        Set this transaction's authorizations to those encoded by the given
        bytestring.
        
        """
        
        # Start with a fresh list of authorizations.
        self.authorizations = []
        
        # How many outputs are there?
        (authorization_count,) = struct.unpack(">I", bytestring[0:4])
        
        # Where are we in the string
        index = 4
        
        for _ in xrange(authorization_count):
            # Get the length of the authorization's public key
            (length,) = struct.unpack(">I", bytestring[index:index + 4])
            index += 4
            
            # Get the public key itself
            public_key = bytestring[index: index + length]
            index += length
            
            # Get the length of the authorization's signature
            (length,) = struct.unpack(">I", bytestring[index:index + 4])
            index += 4
            
            # Get the signature itself
            signature = bytestring[index: index + length]
            index += length
            
            # Add the authorization
            self.authorizations.append((public_key, signature))
        
    def header_bytes(self):
        """
        Convert the inputs and outputs to a bytestring, for signing and for use
        in our encoding.
        
        Packs timestamp in 8 bytes, length of the inputs in 4 bytes, inputs
        bytestring, length of the outputs in 4 bytes, outputs bytestring.
        
        """
        
        # Pack up the inputs
        inputs_packed = self.pack_inputs()
        # And pack up the outputs
        outputs_packed = self.pack_outputs()
        
        # Return both as length-delimited strings
        return "".join([struct.pack(">QI", self.timestamp, len(inputs_packed)),
            inputs_packed, struct.pack(">I", len(outputs_packed)), 
            outputs_packed])
        
    def to_bytes(self):
        """
        Return this Transaction as a bytestring.
        
        Packs the inputs, outputs, and authorizations bytestrings as length-
        delimited strings.
        
        """
        
        # Pack the authorizations
        authorizations_packed = self.pack_authorizations()
        
        # Return the packed inputs and outputs length-delimited strings with one
        # for authorizations on the end.
        return "".join([self.header_bytes(), struct.pack(">I", 
            len(authorizations_packed)), authorizations_packed])
        
    @classmethod
    def from_bytes(cls, bytestring): 
        """
        Make a new Transaction object from a transaction bytestring, as encoded
        by to_bytes.
        
        """
        
        # Make the transaction
        transaction = cls()
        
        # This holds the index we're unpacking the bytestring at
        index = 0
        
        # Get the timestamp
        (transaction.timestamp,) = struct.unpack(">Q", 
            bytestring[index:index + 8])
        index += 8
        
        # Get the length of the inputs bytestring
        (length,) = struct.unpack(">I", bytestring[index:index + 4])
        index += 4
        
        # Get the inputs bytestring
        inputs_bytestring = bytestring[index: index + length]
        index += length
        
        # Get the length of the outputs bytestring
        (length,) = struct.unpack(">I", bytestring[index:index + 4])
        index += 4
        
        # Get the outputs bytestring
        outputs_bytestring = bytestring[index: index + length]
        index += length
        
        # Get the length of the authorizations bytestring
        # TODO: It just runs until the end, so we don't really need this.
        (length,) = struct.unpack(">I", bytestring[index:index + 4])
        index += 4
        
        # Get the authorizations bytestring
        authorizations_bytestring = bytestring[index: index + length]
        index += length   
        
        # Unpack all the individual bytestrings
        transaction.unpack_inputs(inputs_bytestring)
        transaction.unpack_outputs(outputs_bytestring)
        transaction.unpack_authorizations(authorizations_bytestring)
        
        # Return the complete Transaction
        return transaction
        
class CoinState(pybc.State):
    """
    A State that keeps track of all unused outputs in blocks.
    
    """
    
    def __init__(self, unused_outputs=set()):
        """
        Make a new CoinState with no currently unused outputs. Unused outputs
        are identified by the hash of the transaction that created them, the
        index of the output, and the amount of the output, and the hash of the
        destination public key, as a tuple.
        
        A set of unused outputs to wrap may be specified.
        
        """
        
        self.unused_outputs = unused_outputs
        
    def apply_transaction(self, transaction):
        """
        Return a copy of this state with the given Transaction object applied.
        
        """
        
        # Make a set of the unused outputs to add
        to_add = set()
        
        # Make a set of the used outputs to remove
        to_remove = set()
        
        # Get the hash of the transaction
        transaction_hash = transaction.transaction_hash()
        
        for spent_output in transaction.inputs:
            # The inputs are in exactly the same tuple format as we use.
            # Remove each of them from the unused output set.
            to_remove.add(spent_output)
        
        for i, output in enumerate(transaction.outputs):
            # Unpack each output tuple
            amount, destination = output
            
            # Add a record for it to the set of unspent outputs
            to_add.add((transaction_hash, i, amount, 
                destination))
                
        # Remove all the things to remove, add all the things to add, and return
        # a CoinState wrapping the new set.
        return CoinState((self.unused_outputs | to_add) - to_remove)
        
    def remove_transaction(self, transaction):
        """
        Return a copy of this state with the given Transaction object removed.
        
        """
        
        # Make a set of the unused outputs to add
        to_add = set()
        
        # Make a set of the used outputs to remove
        to_remove = set()
        
        # Get the hash of the transaction
        transaction_hash = transaction.transaction_hash()
        
        for spent_output in transaction.inputs:
            # The inputs are in exactly the same tuple format as we use.
            # Add them back to the unused output set.
            to_add.add(spent_output)
        
        for i, output in enumerate(transaction.outputs):
            # Unpack each output tuple
            amount, destination = output
            
            # Remove its record from the set of unspent outputs
            to_remove.add((transaction_hash, i, amount, 
                destination))
                    
        # Remove all the things to remove, add all the things to add, and return
        # a CoinState wrapping the new set.
        return CoinState((self.unused_outputs | to_add) - to_remove)
    
    def step_forwards(self, block):
        """
        Add any outputs of this block's transactions to the set of unused
        outputs, and consume all the inputs.
        
        Returns an updated CoinState.
        """
        
        # Make a set of the unused outputs to add
        to_add = set()
        
        # Make a set of the used outputs to remove
        to_remove = set()
        
        for transaction_bytes in pybc.unpack_transactions(block.payload):
            # Parse the transaction
            transaction = Transaction.from_bytes(transaction_bytes)
        
            # Get the hash of the transaction
            transaction_hash = transaction.transaction_hash()
            
            for spent_output in transaction.inputs:
                # The inputs are in exactly the same tuple format as we use.
                # Remove each of them from the unused output set.
                to_remove.add(spent_output)
            
            for i, output in enumerate(transaction.outputs):
                # Unpack each output tuple
                amount, destination = output
                
                # Add a record for it to the set of unspent outputs
                to_add.add((transaction_hash, i, amount, 
                    destination))
                    
        # Remove all the things to remove, add all the things to add, and return
        # a CoinState wrapping the new set.
        return CoinState((self.unused_outputs | to_add) - to_remove)
        
    def step_backwards(self, block):
        """
        Add any inputs from this block to the set of unused outputs, and remove
        all the outputs.
        
        Returns an updated CoinState.
        """
    
        # Make a set of the unused outputs to add
        to_add = set()
        
        # Make a set of the used outputs to remove
        to_remove = set()
        
        for transaction_bytes in pybc.unpack_transactions(block.payload):
            # Parse the transaction
            transaction = Transaction.from_bytes(transaction_bytes)
            
            # Get the hash of the transaction
            transaction_hash = transaction.transaction_hash()
            
            for spent_output in transaction.inputs:
                # The inputs are in exactly the same tuple format as we use.
                # Add them back to the unused output set.
                to_add.add(spent_output)
            
            for i, output in enumerate(transaction.outputs):
                # Unpack each output tuple
                amount, destination = output
                
                # Remove its record from the set of unspent outputs
                to_remove.add((transaction_hash, i, amount, 
                    destination))
                    
        # Remove all the things to remove, add all the things to add, and return
        # a CoinState wrapping the new set.
        return CoinState((self.unused_outputs | to_add) - to_remove)
            
class CoinBlockchain(pybc.TransactionalBlockchain):
    """
    Represents a Blockchain for a Bitcoin-like currency.
    
    """
    
    def __init__(self, block_store):
        """
        Make a new CoinBlockchain that stores blocks in the specified file.
        
        """
        
        # Just make a new Blockchain using the default POW algorithm and a
        # CoinState to track unspent outputs.
        super(CoinBlockchain, self).__init__(pybc.PowAlgorithm(), block_store, 
            initial_state=CoinState())
            
        # Set up the blockchain for 1 minute blocks, retargeting every 10
        # blocks
        # This is in blocks
        self.retarget_period = 10
        # This is in seconds
        self.retarget_time = self.retarget_period * 60
        
    
    def transaction_valid_for_relay(self, transaction_bytes):
        """
        Say that normal transactions can be accepted from peers, but generation
        and fee collection transactions cannot.
        
        """

        if len(Transaction.from_bytes(transaction_bytes).inputs) > 0:
            # It has an input, so isn't a reward.
            return True
        
        # No inputs. Shouldn't accept this, even if it's valid. It will steal
        # our fees.
        return False
    
    def get_block_reward(self, previous_block):
        """
        Get the block reward for a block based on the given previous block,
        which may be None.
        
        """
        
        # Easy example: 50 coins forever
        
        # Get the height of this block
        if previous_block is not None:
            height = previous_block.height + 1
        else:
            height = 0

        # How many coins should we generate? We could do something based on
        # height, but just be easy.
        coins = 50
        
        # Return the number of coins to generate
        return coins
    
    def verify_transaction(self, transaction_bytes, chain_head, 
        other_transactions=[]):
        """
        If the given Transaction is valid atop the given Block chain_head (which
        may be None) and in light of the already verified other transactions,
        return True. Otherwise, return False.
        
        Ensures that:
        
        The transaction's inputs are existing unspent outputs that the other
        transactions didn't use.
        
        The transaction's authorizations are sufficient to unlock its inputs.
        
        The transaction's outputs do not excede its inputs, if it has inputs.
        
        The transaction's outputs do not excede the left-over coins from all
        previous transactions, if it has no inputs.
         
        """
        
        # First, get the State that must hold after the block we're based on
        state = self.state_after(chain_head)
        
        # How much left-over coin do we have in this block so far? Start with
        # the block reward.
        block_leftover = self.get_block_reward(chain_head)
        
        for other in other_transactions:
            # Parse a Transaction object out
            other_transaction = Transaction.from_bytes(other)
            
            # Add (or remove) the transaction's leftover coins from the block's
            # leftover coins
            block_leftover += other_transaction.get_leftover()
            
            # Apply all the other valid transactions to the state
            state = state.apply_transaction(other_transaction)
            
        # Now we have the state under which this transaction ought to be valid.
        # TODO: Shouldn't we cache it or something?

        try:
            # This holds our parsed transaction
            transaction = Transaction.from_bytes(transaction_bytes)
        except:
            # The transaction is uninterpretable
            print "Uninterpretable transaction."
            traceback.print_exc()
            return False
        
        # Outputs can never be negative since they are unsigned.
        
        if len(transaction.inputs) == 0:
            # This is a fee-collecting/reward-collecting transaction.
            if block_leftover - transaction.get_leftover() < 0:
                # Reject the transaction if it takes more in outputs than the
                # current leftover coins in the block.
                print "Transaction trying to take more than the fee available."
                return False
            else:
                # It has no inputs and can need no verification, so it's fine.
                # TODO: stop people from including useless verifications or
                # something.
                return True
        
        # Now we know the transaction has inputs.
        
        for source in transaction.inputs:
            # Make sure each input is accounted for by a previous unused output.
            if source not in state.unused_outputs:
                # We're trying to spend something that doesn't exist or is
                # already spent.
                print "Transaction trying to use spent or nonexistent input"
                return False
                
        if transaction.get_leftover() < 0:
            # Can't spend more than is available to the transaction.
            print "Transaction trying to output more than it inputs"
            return False
                
        if not transaction.verify_authorizations():
            # The transaction isn't signed properly.
            print "Transaction signature(s) invalid"
            return False
            
        # If we get here, the transaction must be valid. All its inputs are
        # authorized, and its outputs aren't too large.
        return True
        
    def make_block(self, destination, min_fee = 1):
        """
        Override the ordinary Blockchain make_block with a make_block that
        incorporates pending transactions and sends fees to the public key hash
        destination.
        
        min_fee specifies the minimum trnasaction fee to require.
        
        """
        
        # Don't let anybody mess with our transactions and such until we've made
        # the block. It can still be rendered invalid after that, though.
        with self.lock:
        
            # This holds the list of Transaction objects to include
            to_include = []
            
            # This holds the total fee available, starting with the block
            # reward.
            total_fee = self.get_block_reward(self.highest_block)
            
            for transaction_bytes in self.transactions.values():
                # Parse this transaction out.
                transaction = Transaction.from_bytes(transaction_bytes)
                
                # Get how much it pays
                fee = transaction.get_leftover()
                
                if fee >= min_fee:
                    # This transaction pays enough. Use it.
                    to_include.append(transaction)
                    total_fee += fee
            
            # Add a transaction that gives all the generated coins and fees to
            # us.
            reward_transaction = Transaction()
            reward_transaction.add_output(total_fee, destination)
            
            to_include.append(reward_transaction)
            
            # Make a block with the transaction as its payload
            block = super(CoinBlockchain, self).make_block(
                pybc.pack_transactions(
                [transaction.to_bytes() for transaction in to_include]))
                
            return block

class Wallet(object):
    """
    Represents a Wallet that holds keypairs. Interrogates the blockchain to
    figure out what coins are available to spend, and manages available unspent
    outputs and change sending so that you can send transactions for arbitrary
    amounts to arbitrary addresses.
    
    TODO: This isn't thread safe at all.
    
    """
    
    def __init__(self, blockchain, filename):
        """
        Make a new Wallet, working on the given Blockchain, and storing keypairs
        in the given Wallet file.
        
        """
        
        # Use a pdict database to keep pyelliptic ECC objects for our addresses.
        # keypairs are stored by public key hash. Make it not lazy so it saves
        # constantly, so we don't lose keys.
        self.keystore = sqliteshelf.SQLiteShelf(filename, table="wallet")
        
        # Keep the blockchain
        self.blockchain = blockchain
        
        # We need a lock to protect our keystore from multithreaded access.
        # TODO: Shrink the critical sections.
        self.lock = threading.RLock()
    
    def generate_address(self):
        """
        Make a new address and add it to our keystore.
        
        """
        
        # This holds the new keypair as a pyelliptic ECC
        keypair = pyelliptic.ECC()
        
        # Save it to the keystore
        self.keystore[hashlib.sha256(keypair.get_pubkey()).digest()] = keypair
        
    def get_address(self):
        """
        Return the public key hash of an address that we can receive on.
        
        """
        
        with self.lock:
            if len(self.keystore) == 0:
                # We need to make an address
                self.generate_address()    
            
            # Just use the first address we have
            return self.keystore.keys()[0]
        
    def get_spendable_outputs(self):
        """
        Return a collection of all the outputs available to our addresses for
        spending.
        
        """
        
        with self.lock:
            # Accumulate every unused output we have the key for
            spendable_outputs = []
            
            for output in self.blockchain.state.unused_outputs:
                if self.keystore.has_key(output[3]):
                    # We have a key for the output's pubkey hash. We can spend
                    # this.
                    spendable_outputs.append(output)
                    
            # Return all the outputs we can spend.
            return spendable_outputs
    
    def get_balance(self):
        """
        Return the total balance of all spendable outputs.
        
        """
        
        # This holds the balance so far
        balance = 0
        
        for _, _, amount, _ in self.get_spendable_outputs():
            # Sum up the amounts over all spendable outputs
            balance += amount
            
        return balance
        
    def make_simple_transaction(self, amount, destination, fee=1):
        """
        Return a Transaction object sending the given amount to the given
        destination, and any remaining change back to ourselves, leaving the
        specified miner's fee unspent.
        
        If we don't have enough available to spend, return None.
        
        If the amount isn't strictly positive, also returns None, since such a
        transaction would be either useless or impossible depending on the
        actual value.
        
        Destination must be a 32-byte public key SHA256 hash.
        
        A negative fee can be passed, but the resulting transaction will not be
        valid.
        
        """
        
        with self.lock:
        
            if not amount > 0:
                # Transaction is unreasonable: not sending any coins anywhere.
                return None
                
            # Make a transaction
            transaction = Transaction()
            
            # This holds how much we have accumulated from the spendable outputs
            # we've added to the transaction's inputs.
            coins_collected = 0
            
            # This holds the set of public key hashes that we need to sign the
            # transaction with.
            key_hashes = set()
            
            for spendable in self.get_spendable_outputs():
                # Unpack the amount we get from this as an input, and the key we
                # need to use to spend it.
                _, _, input_amount, key_needed = spendable
            
                # Add the unspent output as an input to the transaction
                transaction.add_input(*spendable)
                
                # Say we've collected that many coins
                coins_collected += input_amount
                
                # Say we need to sign with the appropriate key
                key_hashes.add(key_needed)
                
                if coins_collected >= amount + fee:
                    # We have enough coins.
                    break
                    
            if coins_collected < amount + fee:
                # We couldn't find enough money for this transaction!
                return None
                
            # We've made a transaction with enough inputs!
            # Add the outputs.
            # First the amount we actually wanted to send.
            transaction.add_output(amount, destination)
            # Then the change back to us at some address we can receive on.
            transaction.add_output(coins_collected - amount - fee, 
                self.get_address())
            # The fee should be left over.
            
            # Now do the authorizations. What do we need to sign?
            to_sign = transaction.header_bytes()
            
            for key_hash in key_hashes:
                # Load the keypair
                keypair = self.keystore[key_hash]
                
                # Grab the public key
                public_key = keypair.get_pubkey()
                
                # Make the signature
                signature = keypair.sign(to_sign)
                
                # Add the authorization to the transaction
                transaction.add_authorization(public_key, signature)
                
            # Nw the transaction is done!
            return transaction

if __name__ == "__main__":
    # Do a transaction test
    
    def generate_block(blockchain, destination, min_fee = 1):
        """
        Given a blockchain, generate a block (synchronously!), sending the
        generation reward to the given destination public key hash.
        
        min_fee specifies the minimum fee to charge.
        
        TODO: Move this into the Blockchain's get_block method.
        
        """
        
        # Make a block with the transaction as its payload
        block = blockchain.make_block(destination, min_fee=min_fee)
            
        # Now unpack and dump the block for debugging.
        print "Block will be:\n{}".format(block)
        
        for transaction in pybc.unpack_transactions(block.payload):
            # Print all the transactions
            print "Transaction: {}".format(Transaction.from_bytes(transaction))

        # Do proof of work on the block to mine it.
        block.do_work(blockchain.algorithm)
        
        print "Successful nonce: {}".format(block.nonce)
        
        # See if the work really is enough
        print "Work is acceptable: {}".format(block.verify_work(algorithm))
        
        # See if the block is good according to the blockchain
        print "Block is acceptable: {}".format(blockchain.verify_block(block))
        
        # Add it to the blockchain through the complicated queueing mechanism
        blockchain.queue_block(block)
    
    # Make a blockchain
    blockchain = CoinBlockchain("coin.blocks")
    
    # Make a wallet that hits against it
    wallet = Wallet(blockchain, "coin.wallet")
    
    print "Receiving address: {}".format(pybc.bytes2string(
        wallet.get_address()))
    
    # Make a block that gives us coins.
    generate_block(blockchain, wallet.get_address())
    
    # Dump the outputs we can spend
    print "Available outputs:"
    for _, _, amount, destination in wallet.get_spendable_outputs():
        print "\t{} to {}".format(amount, pybc.bytes2string(destination))
        
    # Send some coins to ourselves
    print "Sending ourselves 10 coins..."
    transaction = wallet.make_simple_transaction(10, wallet.get_address())
    print transaction
    blockchain.add_transaction(transaction.to_bytes())
    
    # Make a block that confirms that transaction.
    generate_block(blockchain, wallet.get_address())
    
    # Dump the outputs we can spend now.
    print "Available outputs:"
    for _, _, amount, destination in wallet.get_spendable_outputs():
        print "\t{} to {}".format(amount, pybc.bytes2string(destination))
    
    
