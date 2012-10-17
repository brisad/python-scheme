import operator


class TailRecursion(Exception):
    def __init__(self, next_args):
        self.next_args = next_args


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
        proc_env = Environment(namespace=dict(env.namespace), creator=self)
        while True:
            proc_env.namespace.update(zip(self.parameters, args))
            try:
                result = proc_env.eval(self.function)
            except TailRecursion as tr:
                args = tr.next_args
            else:
                break

        return result

    def __eq__(self, other):
        return self.function == other.function and \
            self.parameters == other.parameters

    def __ne__(self, other):
        return not self.__eq__(other)


class BuiltinProcedure(Procedure):
    def apply(self, env, args):
        return self.function(args)


class Environment(object):
    def __init__(self, namespace=None, special_forms=None, creator=None):
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
        self.creator = creator

    def eval(self, expr, calldepth=0):
        """Evaluate expression.

        Expression is represented by a Expression object.
        """

        if not expr.is_combination():
            try:
                result = self.namespace[expr.scalar]
            except KeyError:
                result = expr.scalar
            return result

        elif expr.fields[0].scalar in self.special_forms:
            f = self.special_forms[expr.fields[0].scalar]
            return f(expr.fields[1:])
        else:
            # 1. Evaluate the subexpressions of the combination
            l = [self.eval(subexpr, calldepth+1) for subexpr in expr.fields]
            # 2. Apply the operator to the operands
            f = l[0]
            if self.creator is f and calldepth == 0:
                raise TailRecursion(l[1:])
            return f.apply(self, l[1:])

    def _define(self, operands):
        """Apply special form 'define' to operands.

        Operands are represented as a list of Expression objects.
        """

        if operands[0].is_combination():
            name = operands[0].fields[0].scalar
            value = Procedure(operands[1],
                              parameters=[x.scalar for x in
                                          operands[0].fields[1:]])
        else:
            name = operands[0].scalar
            value =  self.eval(operands[1])
        self.namespace[name] = value
        return name

    def _cond(self, operands):
        """Apply special form 'cond' to operands.

        Operands are represented as a list of Expression objects.
        """

        for case in operands:
            if not case.fields[0].is_combination() and \
                    case.fields[0].scalar == 'else' or \
                    self.eval(case.fields[0]):
                return self.eval(case.fields[1])
        return False

    def _if(self, operands):
        """Apply special form 'if' to operands.

        Operands are represented as a list of Expression objects.
        """

        return self._cond([Expression([operands[0], operands[1]], True),
                           Expression([Expression('else'), operands[2]], True)])

    def _and(self, operands):
        """Apply special form 'and' to operands.

        Operands are represented as a list of Expression objects.
        """

        for operand in operands:
            last_val = self.eval(operand)
            if not last_val:
                return False
        return last_val

    def _or(self, operands):
        """Apply special form 'or' to operands.

        Operands are represented as a list of Expression objects.
        """

        for operand in operands:
            last_val = self.eval(operand)
            if last_val:
                return last_val
        return False


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
            '+': BuiltinProcedure(cls.add),
            '-': BuiltinProcedure(cls.subtract),
            '*': BuiltinProcedure(cls.multiply),
            '/': BuiltinProcedure(cls.divide),
            'not': BuiltinProcedure(cls.not_),
            '>': BuiltinProcedure(cls.greater_than),
            '<': BuiltinProcedure(cls.less_than),
            '=': BuiltinProcedure(cls.equals)
            }
