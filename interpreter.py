import re

class Interpreter(object):
    def __init__(self, namespace={}, special_forms={}):
        self.namespace = namespace
        self.special_forms = special_forms

    def apply(self, procedure, arguments):
        result = []
        for elem in procedure:
            m = re.search('\((\d)\)', elem)
            if m:
                result.append(arguments[int(m.group(1))])
            else:
                result.append(elem)
        return result

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

            if isinstance(f, list):
                result = self.apply(f, l[1:])
                return self.eval(result)
            else:
                return f(*l[1:])
