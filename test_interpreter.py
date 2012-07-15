from unittest import TestCase, main
from interpreter import Environment, Procedure, Parameter, Builtins

def add(operands):
    return operands[0] + operands[1]

def first(x):
    return x[0]


class test_environment(TestCase):
    def test_eval_numerical_primitive(self):
        env = Environment()
        result = env.eval('123')
        self.assertEquals(123, result)

    def test_eval_numerical_float_primitive(self):
        env = Environment()
        result = env.eval('3.14')
        self.assertEquals(3.14, result)

    def test_eval_variable(self):
        env = Environment(namespace={'var': 123})
        result = env.eval('var')
        self.assertEquals(123, result)

    def test_eval_function(self):
        env = Environment(namespace={'add': add})
        result = env.eval('add')
        self.assertEquals(add, result)

    def test_eval_combination(self):
        env = Environment(namespace={'add': Procedure(add), 'var': 123})
        result = env.eval(['add', 'var', '456'])
        self.assertEquals(579, result)

    def test_eval_nested_combination(self):
        env = Environment(namespace={'add': Procedure(add), 'var': 123})
        result = env.eval(['add', 'var', ['add', '1', '2']])
        self.assertEquals(126, result)

    def test_eval_special_form(self):
        env = Environment(special_forms={'first': first})
        result = env.eval(['first', 'var'])
        self.assertEquals('var', result)

    def test_eval_defined_procedure(self):
        env = Environment(namespace={'add': Procedure(add),
                                     'func': Procedure(['add',
                                                        Parameter(0),
                                                        Parameter(1)])})
        result = env.eval(['func', '1', '2'])
        self.assertEquals(3, result)

    def test_eval_nested_defined_procedure(self):
        env = Environment(namespace={
                'add': Procedure(add),
                'func': Procedure(['add', Parameter(0),
                                   ['add', 20, Parameter(1)]])})
        result = env.eval(['func', '1', '2'])
        self.assertEquals(23, result)

    def test_define(self):
        env = Environment()
        result = env._define(['x', 42])
        self.assertEquals(result, None)
        self.assertEquals(env.namespace['x'], 42)

    def test_if_true(self):
        env = Environment(namespace={'predicate': 1,
                                     'yes': 2,
                                     'no': 3})
        result = env._if(['predicate', 'yes', 'no'])
        self.assertEquals(result, 2)


class test_builtins(TestCase):
    def test_add_three_operands(self):
        result = Builtins.add([1, 2, 3])
        self.assertEquals(6, result)

    def test_subtract_two_operands(self):
        result = Builtins.subtract([3, 2])
        self.assertEquals(1, result)

    def test_subtract_three_operands(self):
        result = Builtins.subtract([3, 2, 1])
        self.assertEquals(0, result)

    def test_subtract_one_operand_negation(self):
        result = Builtins.subtract([1])
        self.assertEquals(-1, result)

    def test_multiply_three_operands(self):
        result = Builtins.multiply([1, 2, 3])
        self.assertEquals(6, result)

    def test_divide_two_operands(self):
        result = Builtins.divide([6, 2])
        self.assertEquals(3, result)

    def test_divide_three_operands(self):
        result = Builtins.divide([12, 3, 2])
        self.assertEquals(2, result)


if __name__ == '__main__':
    main()
