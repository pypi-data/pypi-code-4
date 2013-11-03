import os


class OffsetFilePtr:
    """
    A wrapper for file object to maintain a sub file in original stream.

    :param fp: Original file object.
    :param offset: Start position of the sub file.
    :param total_length: Length of the sub file.
    """
    def __init__(self, fp, offset, total_length):
        self.fp = fp
        self.offset = offset
        self.total_length = total_length

    def read(self, n):
        """
        Read bytes.

        :param n: Count of bytes to read.
        :returns: Bytes.
        """
        return self.fp.read(n)

    def seek(self, pos, mode):
        """
        Seek position in sub file.

        :param pos: Position.
        :param mode: Seek mode.
        """
        if mode == os.SEEK_CUR:
            self.fp.seek(pos, os.SEEK_CUR)
        elif mode == os.SEEK_SET:
            self.fp.seek(self.offset + pos, os.SEEK_SET)
        elif mode == os.SEEK_END:
            self.fp.seek(self.offset + self.total_length + pos, os.SEEK_SET)

    def tell(self):
        """
        Current position in sub file.

        :returns: Current position.
        """
        return self.fp.tell() - self.offset

    def close(self):
        """
        Set internal references to None.

        Note that it will not close the original file object.
        """
        self.fp = None
        self.offset = 0
        self.total_length = 0
