class Visitor(object):

    def visit_integer(self, expression_1):
        pass

    def visit_float(self, expression_1):
        pass

    def visit_add(self, expression_1, expression_2):
        pass

    def visit_subtract(self, expression_1, expression_2):
        pass

    def visit_multiply(self, expression_1, expression_2):
        pass

    def visit_divide(self, expression_1, expression_2):
        pass

    def visit(self, node):
        if node[0] == 'INTEGER':
            return self.visit_integer(node[1])
        if node[0] == 'FLOAT':
            return self.visit_float(node[1])
        if node[0] == 'ADD':
            return self.visit_add(self.visit(node[1]), self.visit(node[2]))
        if node[0] == 'SUBTRACT':
            return self.visit_subtract(self.visit(node[1]), self.visit(node[2]))
        if node[0] == 'MULTIPLY':
            return self.visit_multiply(self.visit(node[1]), self.visit(node[2]))
        if node[0] == 'DIVIDE':
            return self.visit_divide(self.visit(node[1]), self.visit(node[2]))
