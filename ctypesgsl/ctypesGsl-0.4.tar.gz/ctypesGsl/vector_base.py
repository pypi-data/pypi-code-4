"""Base class for vectors."""


class vector_base:
    def __len__(self):
        return int(self.ptr.contents.size)
    def __iter__(self):
        def vec_iter(v):
            for i in range(len(v)):
                yield v[i]
        return vec_iter(self)

    def __str__(self):
        return "[" + ", ".join([str(x) for x in self]) + "]"
