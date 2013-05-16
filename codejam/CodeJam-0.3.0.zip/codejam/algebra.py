from sympy import Matrix as SympyMatrix

class Matrix(SympyMatrix):
    def __mod__(self, m):           # Modulo was missing from Sympy matrices
        func = lambda i, j: self[i, j] % m
        return Matrix(self.rows, self.cols, func)
