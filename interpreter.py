import operator

class Procedure(object):
    def __init__(self, function):
        self.function = function

    def apply(self, interpreter, args):
        try:
            result = self.function(*args)
        except TypeError:
            # Replace all parameters in with values of the arguments
            func = [self._replace(x, args) for x in self.function]
            result = interpreter.eval(func)
        return result

    def _replace(self, elem, args):
        """Replace element with parameter if applicable."""
        if isinstance(elem, Parameter):
            # If elem is a parameter, return the value of the argument
            return args[elem.index]
        elif isinstance(elem, list):
            return [self._replace(x, args) for x in elem]
        else:
            return elem
            

class Parameter(object):
    def __init__(self, index=0):
        self.index = index


class Environment(object):
    def __init__(self, namespace=None, special_forms=None):
        if namespace is None:
            namespace = {}
        if special_forms is None:
            special_forms = {}

        self.namespace = namespace
        self.special_forms = special_forms

    def eval(self, expr):

        if not isinstance(expr, list):
            try:
                result = float(expr) if '.' in expr else int(expr)
            except ValueError:
                # symbol
                result = self.namespace.get(expr)
            except TypeError:
                # already numeral, evaluates to itself
                result = expr
            return result

        elif expr[0] in self.special_forms:
            f = self.special_forms[expr[0]]
            return f(expr[1:])
        else:
            # 1. Evaluate the subexpressions of the combination
            l = [self.eval(subexpr) for subexpr in expr]
            # 2. Apply the operator to the operands
            f = l[0]
            return f.apply(self, l[1:])


class Builtins(object):
    @classmethod
    def add(self, operands):
        return sum(operands)

    @classmethod
    def subtract(self, operands):
        if len(operands) == 1:
            return -operands[0]
        return operands[0] - sum(operands[1:])

    @classmethod
    def multiply(self, operands):
        return reduce(operator.mul, operands)

    @classmethod
    def divide(self, operands):
        return operands[0] / sum(operands[1:])

    @classmethod
    def namespace(cls):
        return {
            '+': Procedure(cls.add),
            '-': Procedure(cls.subtract),
            '*': Procedure(cls.multiply),
            '/': Procedure(cls.divide)
            }
