class Matrix(object):

    def __init__(self, matrix):
        self.matrix = matrix

    def get_dim(self, dim):
        """Returns the number of rows or columns a given matrix has.
        
        >>> a = matrix(row(1, 2), row(3, 4), row(5, 6))
        >>> Matrix(a).get_dim("rows")
        3
        >>> Matrix(a).get_dim("cols")
        2
        """
        if dim == "rows":
            return len(self.matrix)
        elif dim == "cols":
            return len(self.matrix[0])

    def get_row(self, row):
        """Takes in a matrix in list form and returns the matrix row inputed in as "row".

        >>> a = matrix([1, 0], [0, 1])
        >>> Matrix(a).get_row(2)
        [0, 1]
        """
        return self.matrix[row-1]

    def get_col(self, col):
        """Same concept as get_row, except with columns of a matrix.

        >>> a = matrix([1, 2], [3, 4])
        >>> Matrix(a).get_col(1)
        [1, 3]
        """
        c = []
        for x in self.matrix:
            c.append(x[col-1])
        return c

    def del_row(self, row):
        """Removes a specified row of a matrix.
    
        >>> a = matrix([1, 2], [3, 4])
        >>> Matrix(a).del_row(1)
        [[3, 4]]
        """
        a = self.matrix
        del a[row-1]
        return a

    def del_col(self, col):
        """Removes a specified column of a matrix.

        >>> a = matrix([1, 2], [3, 4])
        >>> Matrix(a).del_col(1)
        [[2], [4]]
        """
        a = self.matrix
        for row in a:
            del row[col-1]
        return a

    def get_element(self, row, column):
        """Returns a single element of a matrix.
        
        >>> a = matrix([1, 2], [3, 4])
        >>> Matrix(a).get_element(2, 1)
        3
        """
        return Matrix(self.matrix).get_row(row)[column-1]

    def copy(self):
        """Returns a copy of a matrix so that you can mutate one copy and maintain the state of the other.

        >>> a = matrix([1, 2], [3, 4])
        >>> b = Matrix(a).copy()
        >>> Matrix(b).del_row(1)
        [[3, 4]]
        >>> a
        [[1, 2], [3, 4]]
        """
        import copy
        return copy.deepcopy(self.matrix)

    def transpose(self):
        """Transposes a matrix.

        >>> a = matrix([1, 2], [3, 4])
        >>> Matrix(a).transpose()
        [[1, 3], [2, 4]]
        """
        t_mat = []
        for x in range(1, Matrix(self.matrix).get_dim("cols")+1):
            t_mat.append(Matrix(self.matrix).get_col(x))
        return t_mat

#############################################

class MatOperators(object):

    def add_matrices(self, x, y):
        """Adds two matrices of the same dimensions.

        >>> matrix1 = matrix(row(1, 2), row(3, 4))
        >>> matrix2 = matrix(row(2, 3), row(4, 5))
        >>> MatOperators().add_matrices(matrix1, matrix2)
        [[3, 5], [7, 9]]
        """
        assert Matrix(x).get_dim("rows") == Matrix(y).get_dim("rows") and Matrix(x).get_dim("cols") == Matrix(y).get_dim("cols"), "Please select two matrices of the same dimensions"
 
        z = []
        for row_x, row_y in zip(x, y):
            z.append([a+b for a, b in zip(row_x, row_y)])
        return z

    def scalar_mul(self, a, scalar):
        """Multiplies a matrix by a scalar value.

        >>> row1, row2 = row(1, 0), row(0, 1)
        >>> a = matrix(row1, row2)
        >>> MatOperators().scalar_mul(a, 3)
        [[3, 0], [0, 3]]
        """
        return [[elem * scalar for elem in row] for row in a]

    def mul_matrices(self, x, y):
        """Multiplies two matrices of corresponding dimensions.

        >>> matrix1 = matrix(row(1, 2), row(3, 4))
        >>> matrix2 = matrix(row(2, 3), row(4, 5))
        >>> MatOperators().mul_matrices(matrix1, matrix2)
        [[10, 13], [22, 29]]
        """
        assert Matrix(x).get_dim("cols") == Matrix(y).get_dim("rows"), "Please choose a valid pair of matrices to multiply."

        z = []
        y = Matrix(y).transpose()
        for row_x in x:
            p_row = []
            for col_y in y:
                product = 0
                for a, b in zip(row_x, col_y):
                    product += a*b
                p_row.append(product)
            z.append(p_row)
        return z

#############################################

def row(*args):
    """Creates an individual row of a matrix.

    >>> row(1, 2, 3, 4, 5)
    [1, 2, 3, 4, 5]
    """
    r = []
    for arg in args:
        r.append(arg)
    return r

def matrix(*args):
    """Input arguments as rows in list form to construct a functional matrix.
    
    >>> row1, row2 = row(1, 0), row(0, 1)
    >>> matrix(row1, row2)
    [[1, 0], [0, 1]]
    """
    a = []
    for arg in args:
        a.append(arg)
    return a

#############################################
############ ABSTRACTION BARRIER ############
############################################# 

def print_matrix(a):
    """Prints a list-formed matrix in a readable form."""
    rows = Matrix(a).get_dim("rows")
    for row in range(rows):
        print(Matrix(a).get_row(row+1))

def sub_matrices(x, y):
    """Subtracts two matrices of the same dimensions.

    >>> matrix1 = matrix(row(1, 2), row(3, 4))
    >>> matrix2 = matrix(row(2, 3), row(4, 5))
    >>> sub_matrices(matrix1, matrix2)
    [[-1, -1], [-1, -1]]
    """
    y = MatOperators().scalar_mul(y, -1)
    return MatOperators().add_matrices(x, y) 

def determinant(a):
    """Returns the determinant of an nxn matrix.
    
    >>> a = matrix(row(1, 2, 3), row(4, 5, 6), row(7, 8, 1))
    >>> determinant(a)
    24
    """
    coord = Matrix(a).get_element

    def helper(col):
        b = Matrix(a).copy()
        Matrix(b).del_row(1)
        Matrix(b).del_col(col)
        return b

    def cofactor(m, n):
        b = helper(n)
        return (-1)**(m + n) * determinant(b)

    if Matrix(a).get_dim("rows") == 2 and Matrix(a).get_dim("cols") == 2:
        return coord(1, 1) * coord(2, 2) - coord(1, 2) * coord(2, 1)

    total = 0
    for col in range(Matrix(a).get_dim("cols")):
        total += coord(1, col+1) * cofactor(1, col+1)

    return total
