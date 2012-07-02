class Interpreter(object):
    def __init__(self, namespace={}, special_forms={}):
        self.namespace = namespace
        self.special_forms = special_forms

    def eval(self, expression):

        if not isinstance(expression, list):
            try:
                result = int(expression)
            except ValueError:
                result = self.namespace.get(expression)
            return result

        elif expression[0] in self.special_forms:
            f = self.special_forms[expression[0]]
            return f(expression[1:])
        else:
            # 1. Evaluate the subexpressions of the combination
            l = [self.eval(subexpr) for subexpr in expression]
            # 2. Apply the operator to the operands
            f = l[0]
            return f(*l[1:])
