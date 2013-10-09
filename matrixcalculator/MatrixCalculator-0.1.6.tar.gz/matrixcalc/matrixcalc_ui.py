from matrixcalc import matrixcalc
version = "v0.1.6"

def template(m, n):
    position = 11
    matrix = [[elem for elem in range(row*10+1, n+(row*10+1))] for row in range(1, m+1)]

    for row in matrix:
        print(row)

def prompt_row():
    """Allows for user row input."""
    construct = "matrixcalc.row("
    construct += input()
    return eval(construct + ")")

def construct_matrix(letter, rows):
    construct = "matrixcalc.matrix("
    for row in range(1, rows+1):
        print("Please input the entries of Matrix %s, separated by commas, for row %s." % (letter, row))
        construct += str(prompt_row()) + ", "
    return eval(construct + ")")

#################################################

class Interface(object):

    def menu(self):
        print("Welcome to MatrixCalculator %s" % version)
        print("""
        1. Add matrices
        2. Subtract matrices
        3. Multiply matrices
        4. Scalar multiply matrices
        5. Transpose a matrix
        6. Find determinant of a matrix
        7. Find inverse of a matrix
        8. Exit
        """)

        selection = input("Please input the number of your selection: ")
    
        def navigate(selection):
            if selection == "1":
                return Interface().add_or_sub(matrixcalc.MatOperators().add_matrices)
            elif selection == "2":
                return Interface().add_or_sub(matrixcalc.sub_matrices)
            elif selection == "3":
                return Interface().mul()
            elif selection == "4":
                return Interface().scalar_mul()
            elif selection == "5":
                return Interface().transpose()
            elif selection == "6":
                return Interface().det()
            elif selection == "7":
                return Interface().inverse()
            elif selection == "8":
                exit()

            selection = input("Input not recognized. Please re-enter your selection: ")
            navigate(selection)

        navigate(selection)

    def add_or_sub(self, operator):
        rows = int(input("\nHow many rows are in your matrices? "))
        cols = int(input("How many columns are in your matrices? "))

        print()
        template(rows, cols)
        print()
        
        a = construct_matrix("A", rows)
        print()
        b = construct_matrix("B", rows)

        ab = operator(a, b)

        print("\nAnswer:")
        matrixcalc.print_matrix(ab)

        input("\nPress ENTER to return to the menu\n")
        Interface().menu()

    def mul(self):
        row1 = int(input("\nHow many rows are in Matrix A? "))
        col1 = int(input("How many columns are in Matrix A? "))

        row2 = int(input("\nHow many rows are in Matrix B? "))
        col2 = int(input("How many columns are in Matrix B? "))

        print()
        template(row1, col1)
        print()

        a = construct_matrix("A", row1)

        print()
        template(row2, col2)
        print()

        b = construct_matrix("B", row2)
        ab = matrixcalc.MatOperators().mul_matrices(a, b)

        print("\nThe product of Matrix A and Matrix B is:")
        matrixcalc.print_matrix(ab)

        input("\nPress ENTER to return to the menu\n")
        Interface().menu()

    def scalar_mul(self):
        rows = int(input("\nHow many rows are in your matrix? "))
        cols = int(input("How many columns are in your matrix? "))
        scalar = int(input("What scalar are you multiplying your matrix by? "))

        print()
        template(rows, cols)
        print()

        a = construct_matrix("A", rows)
        scalar_a = matrixcalc.MatOperators().scalar_mul(a, scalar)

        print("\nThe scalar product of Matrix A is:")
        matrixcalc.print_matrix(scalar_a)

        input("\nPress ENTER to return to the menu\n")
        Interface().menu()

    def transpose(self):
        rows = int(input("\nHow many rows are in your matrix? "))
        cols = int(input("How many columns are in your matrix? "))

        print()
        template(rows, cols)
        print()

        a = construct_matrix("A", rows)
        transpose_a = matrixcalc.Matrix(a).transpose()

        print("\nThe tranposed matrix of Matrix A is:")
        matrixcalc.print_matrix(transpose_a)

        input("\nPress ENTER to return to the menu\n")
        Interface().menu()

    def det(self):
        rows = int(input("\nHow many rows and columns are in your matrix? "))

        print()
        template(rows, rows)
        print()

        a = construct_matrix("A", rows)
        det_a = matrixcalc.determinant(a)

        print("\nThe determinant of Matrix A is: %s" % det_a)

        input("\nPress ENTER to return to the menu\n")
        Interface().menu()

    def inverse(self):
        rows = int(input("\nHow many rows and columns are in your matrix? "))

        print()
        template(rows, rows)
        print()

        a = construct_matrix("A", rows)
        inverse_a = matrixcalc.inverse(a)

        print("\nThe inverse of Matrix A is:")
        matrixcalc.print_matrix(inverse_a)

        input("\nPress ENTER to return to the menu\n")
        Interface().menu()
