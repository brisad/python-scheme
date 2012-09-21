import operator


class Expression(object):
    def __init__(self, contents, combination=False):
        if combination:
            self.scalar = None
            self.fields = contents
        else:
            self.scalar = contents
            self.fields = None

    def is_combination(self):
        return self.fields is not None

    @classmethod
    def create(self, expr):
        """Create a Expression object from a list expression.

        Traverse the expression tree expr and create a new tree with
        Expression objects instead.
        """

        if isinstance(expr, list):
            return Expression([self.create(field) for field in expr], True)
        else:
            return Expression(expr)

    def __eq__(self, other):
        try:
            if self.is_combination() and other.is_combination() and \
                    len(self.fields) == len(other.fields):
                return all(x == y for x, y in zip(self.fields, other.fields))
            elif not self.is_combination() and not other.is_combination():
                return self.scalar == other.scalar
        except AttributeError:
            pass
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


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
                             'if': self._if,
                             'cond': self._cond,
                             'and': self._and,
                             'or': self._or}

        self.namespace = namespace
        self.special_forms = special_forms

    def eval(self, expr):

        if not isinstance(expr, list):
            try:
                result = self.namespace[expr]
            except KeyError:
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
            self.namespace[operands[0]] = self.eval(operands[1])

    def _cond(self, operands):
        index = 0
        try:
            while operands[index][0] != 'else' \
                    and not self.eval(operands[index][0]):
                index += 1
        except IndexError:
            # We will end up here if all predicates evaluate to false
            pass
        else:
            return self.eval(operands[index][1])

    def _if(self, operands):
        if self.eval(operands[0]):
            return self.eval(operands[1])
        else:
            return self.eval(operands[2])

    def _and(self, operands):
        index = 0
        try:
            value = self.eval(operands[index])
            while value:
                index += 1
                value = self.eval(operands[index])
        except IndexError:
            return value
        else:
            return False

    def _or(self, operands):
        index = 0
        try:
            value = self.eval(operands[index])
            while not value:
                index += 1
                value = self.eval(operands[index])
        except IndexError:
            return False
        else:
            return value


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
    def not_(self, operands):
        return not operands[0]

    @classmethod
    def greater_than(cls, operands):
        return operands[0] > operands[1]

    @classmethod
    def less_than(cls, operands):
        return operands[0] < operands[1]

    @classmethod
    def equals(cls, operands):
        return operands[0] == operands[1]


    @classmethod
    def namespace(cls):
        return {
            '+': Procedure(cls.add),
            '-': Procedure(cls.subtract),
            '*': Procedure(cls.multiply),
            '/': Procedure(cls.divide),
            'not': Procedure(cls.not_),
            '>': Procedure(cls.greater_than),
            '<': Procedure(cls.less_than),
            '=': Procedure(cls.equals)
            }
