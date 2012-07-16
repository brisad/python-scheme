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
        self.assertEqual(123, result)

    def test_eval_numerical_float_primitive(self):
        env = Environment()
        result = env.eval('3.14')
        self.assertEqual(3.14, result)

    def test_eval_variable(self):
        env = Environment(namespace={'var': 123})
        result = env.eval('var')
        self.assertEqual(123, result)

    def test_eval_function(self):
        env = Environment(namespace={'add': add})
        result = env.eval('add')
        self.assertEqual(add, result)

    def test_eval_combination(self):
        env = Environment(namespace={'add': Procedure(add), 'var': 123})
        result = env.eval(['add', 'var', '456'])
        self.assertEqual(579, result)

    def test_eval_nested_combination(self):
        env = Environment(namespace={'add': Procedure(add), 'var': 123})
        result = env.eval(['add', 'var', ['add', '1', '2']])
        self.assertEqual(126, result)

    def test_eval_special_form(self):
        env = Environment(special_forms={'first': first})
        result = env.eval(['first', 'var'])
        self.assertEqual('var', result)

    def test_eval_defined_procedure(self):
        env = Environment(namespace={'add': Procedure(add),
                                     'func': Procedure(['add',
                                                        Parameter(0),
                                                        Parameter(1)])})
        result = env.eval(['func', '1', '2'])
        self.assertEqual(3, result)

    def test_eval_nested_defined_procedure(self):
        env = Environment(namespace={
                'add': Procedure(add),
                'func': Procedure(['add', Parameter(0),
                                   ['add', 20, Parameter(1)]])})
        result = env.eval(['func', '1', '2'])
        self.assertEqual(23, result)

    def test_define(self):
        env = Environment()
        result = env._define(['x', 42])
        self.assertEqual(result, None)
        self.assertEqual(env.namespace['x'], 42)

    def test_if_true(self):
        env = Environment(namespace={'predicate': 1,
                                     'yes': 2,
                                     'no': 3})
        result = env._if(['predicate', 'yes', 'no'])
        self.assertEqual(result, 2)


class test_builtins(TestCase):
    def test_add_three_operands(self):
        result = Builtins.add([1, 2, 3])
        self.assertEqual(6, result)

    def test_subtract_two_operands(self):
        result = Builtins.subtract([3, 2])
        self.assertEqual(1, result)

    def test_subtract_three_operands(self):
        result = Builtins.subtract([3, 2, 1])
        self.assertEqual(0, result)

    def test_subtract_one_operand_negation(self):
        result = Builtins.subtract([1])
        self.assertEqual(-1, result)

    def test_multiply_three_operands(self):
        result = Builtins.multiply([1, 2, 3])
        self.assertEqual(6, result)

    def test_divide_two_operands(self):
        result = Builtins.divide([6, 2])
        self.assertEqual(3, result)

    def test_divide_three_operands(self):
        result = Builtins.divide([12, 3, 2])
        self.assertEqual(2, result)


class test_procedure(TestCase):
    def test_equality_true(self):
        p1 = Procedure(add)
        p2 = Procedure(add)
        p3 = Procedure(['foo', Parameter(0)])
        p4 = Procedure(['foo', Parameter(0)])

        self.assertEqual(p1, p2)
        self.assertEqual(p3, p4)

    def test_equality_false(self):
        p1 = Procedure(add)
        p2 = Procedure(sum)
        p3 = Procedure(['foo', Parameter(0)])
        p4 = Procedure(['foo', Parameter(1)])
        p5 = Procedure(['bar', Parameter(0)])

        self.assertNotEqual(p1, p2)
        self.assertNotEqual(p3, p4)
        self.assertNotEqual(p4, p5)


class test_parameter(TestCase):
    def test_equality_true(self):
        p1 = Parameter(0)
        p2 = Parameter(0)
        self.assertEqual(p1, p2)

    def test_equality_false(self):
        p1 = Parameter(0)
        p2 = Parameter(1)
        self.assertNotEqual(p1, p2)


if __name__ == '__main__':
    main()
