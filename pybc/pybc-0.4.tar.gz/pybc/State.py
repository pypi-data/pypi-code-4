"""
State.py: contains the base State class.

"""

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
