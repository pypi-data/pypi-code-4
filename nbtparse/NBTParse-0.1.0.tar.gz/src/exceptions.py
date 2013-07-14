class MalformedNBTError(Exception):
    """Base class of all exceptions caused by malformed or invalid NBT.
    
    NBT does not provide any easy method to recover from this sort of error.

    The source file's offset pointer is not reset, because it might not be
    possible to do so.  If you want to seek back to the beginning, do so
    manually.
    """
    pass


class NoSuchTagTypeError(MalformedNBTError):
    """Raised if an unrecognized tag type is used."""
    pass


class IncompleteSequenceError(MalformedNBTError):
    """Raised if a sequence is incomplete (i.e. we hit EOF too early)."""
    pass
