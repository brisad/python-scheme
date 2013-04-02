import random
import time
import operator


class TailCall(Exception):
    def __init__(self, expr, namespace):
        self.expr = expr
        self.namespace = namespace


class SymbolError(Exception):
    pass


class Expression(object):

    """Store expressions

    Expressions can be of different types, where the actual type
    together with the contents is set at instantiation.

    Public methods:
    is_constant() -- return True if expression is a constant
    is_name() -- return True if expression is a name
    is_combination() -- return True if expression is a combination

    Instance variables:
    type_ -- type of expression
    fields -- contents of expression if type is a combination
    scalar -- contents of expression if type is a constant or name

    """

    CONSTANT, NAME, COMBINATION = range(3)
    def __init__(self, contents, type_=NAME):
        self.type_ = type_
        self.contents = contents

    @property
    def scalar(self):
        if self.type_ != self.CONSTANT and self.type_ != self.NAME:
            raise AttributeError(
                "This Expression type has no scalar attribute")
        return self.contents

    @property
    def fields(self):
        if self.type_ != self.COMBINATION:
            raise AttributeError(
                "This Expression type has no fields attribute")
        return self.contents

    def is_constant(self):
        return self.type_ == self.CONSTANT

    def is_name(self):
        return self.type_ == self.NAME

    def is_combination(self):
        return self.type_ == self.COMBINATION

    def __eq__(self, other):
        try:
            if self.type_ != other.type_:
                return False
        except AttributeError:
            # This exception will be raised if we are comparing with
            # an object that doesn't have the type_ attribute.
            return False

        if self.is_combination() and len(self.fields) == len(other.fields):
            return all(x == y for x, y in zip(self.fields, other.fields))
        else:
            return self.scalar == other.scalar

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        typename = ("CONSTANT", "NAME", "COMBINATION")[self.type_]
        if self.is_combination():
            contents = self.fields
        else:
            contents = self.scalar
        return "%s(%r, %s)" % (self.__class__.__name__, contents, typename)

    def __str__(self):
        if self.is_combination():
            elem = []
            # To get nicer output, run str() on all elements which are
            # instances of Expression.
            for field in self.fields:
                if isinstance(field, self.__class__):
                    elem.append(str(field))
                else:
                    elem.append(repr(field))
            result = '[%s]' % ', '.join(elem)
        else:
            result = '%r' % self.scalar
        return result


class Procedure(object):
    def __init__(self, function, parameters=None):
        self.function = function
        self.parameters = parameters

    def apply(self, env, args, eliminate_tail_call=False):
        proc_env = Environment(namespace=dict(env.namespace), creator=self)
        proc_env.namespace.update(zip(self.parameters, args))
        for f in self.function[:-1]:
            proc_env.eval(f)
        if eliminate_tail_call:
            raise TailCall(self.function[-1], proc_env.namespace)
        else:
            result = proc_env.eval(self.function[-1])
        return result

    def __eq__(self, other):
        return self.function == other.function and \
            self.parameters == other.parameters

    def __ne__(self, other):
        return not self.__eq__(other)


class DummyStream:
    def read(self, data):
        pass

    def write(self, data):
        pass


class BuiltinProcedure(object):
    def __init__(self, function, needs_stream=False, stream=None):
        self.function = function
        self.needs_stream = needs_stream
        if needs_stream:
            if stream is None:
                stream = DummyStream()
                self.uses_dummy = True
            else:
                self.uses_dummy = False
        else:
            stream = None
        self.stream = stream

    def apply(self, env, args, eliminate_tail_call=False):
        if self.needs_stream:
            return self.function(args, self.stream)
        else:
            return self.function(args)

    def __eq__(self, other):
        if self.function != other.function:
            return False
        if self.needs_stream and other.needs_stream:
            if self.uses_dummy and other.uses_dummy:
                return True
            else:
                return self.stream == other.stream
        else:
            return self.needs_stream == other.needs_stream

    def __ne__(self, other):
        return not self.__eq__(other)


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

    def eval(self, expr):
        """Evaluate expression.

        Expression is represented by an Expression object.

        """

        saved_namespace = self.namespace
        while True:
            try:
                result = self._evaluate(expr)
            except TailCall as tc:
                expr = tc.expr
                self.namespace = tc.namespace
            else:
                break

        self.namespace = saved_namespace

        return result

    def _evaluate(self, expr):
        if expr.is_name():
            try:
                result = self.namespace[expr.scalar]
            except KeyError:
                raise SymbolError('%s undefined' % expr.scalar)
            return result
        elif expr.is_constant():
            return expr.scalar
        elif expr.fields[0].scalar in self.special_forms:
            f = self.special_forms[expr.fields[0].scalar]
            return f(expr.fields[1:])
        else:
            # 1. Evaluate the subexpressions of the combination
            l = [self.eval(subexpr) for subexpr in expr.fields]
            # 2. Apply the operator to the operands
            f = l[0]
            return f.apply(self, l[1:], eliminate_tail_call=True)

    def _define(self, operands):
        """Apply special form 'define' to operands.

        Operands are represented as a list of Expression objects.

        """

        if operands[0].is_combination():
            name = operands[0].fields[0].scalar
            value = Procedure(operands[1:],
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
                for expr in case.fields[1:-1]:
                    self.eval(expr)
                return self.eval(case.fields[-1])
        return None

    def _if(self, operands):
        """Apply special form 'if' to operands.

        Operands are represented as a list of Expression objects.

        """

        expr = [Expression([operands[0], operands[1]],
                           Expression.COMBINATION)]
        if len(operands) > 2:
            expr.append(Expression([Expression('else'), operands[2]],
                                   Expression.COMBINATION))
        return self._cond(expr)

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
    def abs(cls, operands):
        return abs(operands[0])

    @classmethod
    def remainder(cls, operands):
        return operands[0] % operands[1]

    @classmethod
    def newline(cls, operands, stream):
        stream.write('\n')

    @classmethod
    def display(cls, operands, stream):
        stream.write(str(operands[0]))

    @classmethod
    def runtime(cls, operands):
        return int(time.time() * 1000000)

    @classmethod
    def random(cls, operands):
        return random.randint(0, operands[0] - 1)

    @classmethod
    def namespace(cls, outstream=None):
        return {
            'true': True,
            'false': False,
            '+': BuiltinProcedure(cls.add),
            '-': BuiltinProcedure(cls.subtract),
            '*': BuiltinProcedure(cls.multiply),
            '/': BuiltinProcedure(cls.divide),
            'not': BuiltinProcedure(cls.not_),
            '>': BuiltinProcedure(cls.greater_than),
            '<': BuiltinProcedure(cls.less_than),
            '=': BuiltinProcedure(cls.equals),
            'abs': BuiltinProcedure(cls.abs),
            'remainder': BuiltinProcedure(cls.remainder),
            'newline': BuiltinProcedure(cls.newline, True, outstream),
            'display': BuiltinProcedure(cls.display, True, outstream),
            'runtime': BuiltinProcedure(cls.runtime),
            'random': BuiltinProcedure(cls.random)
        }
