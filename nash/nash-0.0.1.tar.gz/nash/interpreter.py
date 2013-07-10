from . import visitor as visitor

class Interpreter(visitor.Visitor):
    def visit_add(self, expression_1, expression_2):
        return expression_1 + expression_2
    def visit_subtract(self, expression_1, expression_2):
        return expression_1 - expression_2
    def visit_multiply(self, expression_1, expression_2):
        return expression_1 * expression_2
    def visit_divide(self, expression_1, expression_2):
        return expression_1 / expression_2
    def visit_integer(self, expression_1):
        return expression_1
    def visit_float(self, expression_1):
        return expression_1

