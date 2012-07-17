import operator
from parser import Parser

class Procedure(object):
    def __init__(self, function, parameters=None):
        self.function = function
        self.parameters = parameters

    def apply(self, env, args):
        try:
            result = self.function(args)
        except TypeError:
            proc_env = Environment(namespace=dict(env.namespace))
            proc_env.namespace.update(zip(self.parameters, args))
            result = proc_env.eval(self.function)
        return result

    def __eq__(self, other):
        return self.function == other.function and \
            self.parameters == other.parameters

    def __ne__(self, other):
        return not self.__eq__(other)


class Environment(object):
    def __init__(self, namespace=None, special_forms=None):
        if namespace is None:
            namespace = {}
        if special_forms is None:
            special_forms = {'define': self._define,
                             'if': self._if}

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

    def _define(self, operands):
        if isinstance(operands[0], list):
            name = operands[0][0]
            self.namespace[name] = Procedure(operands[1],
                                             parameters=operands[0][1:])
        else:
            self.namespace[operands[0]] = operands[1]

    def _if(self, operands):
        if self.eval(operands[0]):
            return self.eval(operands[1])
        else:
            return self.eval(operands[2])


class Builtins(object):
    @classmethod
    def add(cls, operands):
        return sum(operands)

    @classmethod
    def subtract(cls, operands):
        if len(operands) == 1:
            return -operands[0]
        return operands[0] - sum(operands[1:])

    @classmethod
    def multiply(cls, operands):
        return reduce(operator.mul, operands)

    @classmethod
    def divide(cls, operands):
        return operands[0] / sum(operands[1:])

    @classmethod
    def namespace(cls):
        return {
            '+': Procedure(cls.add),
            '-': Procedure(cls.subtract),
            '*': Procedure(cls.multiply),
            '/': Procedure(cls.divide)
            }


class Interpreter(object):
    def __init__(self):
        self.parser = Parser()
        self.environment = Environment(namespace=Builtins.namespace())

    def eval(self, inp):
        parsed = self.parser.parse(inp)
        for expression in parsed:
            yield self.environment.eval(expression)


if __name__ == '__main__':
    interp = Interpreter()

    try:
        while True:
            for result in interp.eval(raw_input()):
                print result
    except KeyboardInterrupt:
        pass
