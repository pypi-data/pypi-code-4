"""Base class for matrices."""


class matrix_base:
    def size(self):
        return self.shape

    def __str__(self):
        mat_str = ""
        m, n = self.shape
        for i in xrange(m):
            row_str = ""
            if m == 1:
                row_str += "("
            else:
                if i == 0:
                    row_str += "/"
                elif i == m - 1:
                    row_str += "\\"
                else:
                    row_str += "|"
            row_str += ", ".join([str(self[(i, j)]) for j in xrange(n)])
            if m == 1:
                row_str += ")"
            else:
                if i == 0:
                    row_str += "\\"
                elif i == m - 1:
                    row_str += "/"
                else:
                    row_str += "|"
            row_str += "\n"
            mat_str += row_str
        return mat_str
