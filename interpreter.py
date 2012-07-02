class Interpreter(object):
    def __init__(self, namespace={}):
        self.namespace = namespace

    def eval(self, expression):

        if not isinstance(expression, list):
            try:
                result = int(expression)
            except ValueError:
                result = self.namespace.get(expression)
            return result

        else:
            # 1. Evaluate the subexpressions of the combination
            l = [self.eval(subexpr) for subexpr in expression]
            # 2. Apply the operator to the operands
            f = l[0]
            return f(*l[1:])
