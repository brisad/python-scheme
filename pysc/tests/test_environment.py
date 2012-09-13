from unittest import TestCase, main
from pysc.environment import Environment, Procedure, Builtins

def add(operands):
    return operands[0] + operands[1]

def first(x):
    return x[0]


class test_environment(TestCase):
    def setUp(self):
        self.env = Environment()

    def set_namespace(self, namespace):
        self.env.namespace = namespace

    def assert_eval_results(self, inp, outp):
        result = self.env.eval(inp)
        self.assertEqual(outp, result)

    def test_eval_numerical_primitive(self):
        self.assert_eval_results(123, 123)

    def test_eval_numerical_float_primitive(self):
        self.assert_eval_results(3.14, 3.14)

    def test_eval_variable(self):
        self.set_namespace({'var': 123})
        self.assert_eval_results('var', 123)

    def test_eval_function(self):
        self.set_namespace({'add': add})
        self.assert_eval_results('add', add)

    def test_eval_combination(self):
        self.set_namespace({'add': Procedure(add), 'var': 123})
        self.assert_eval_results(['add', 'var', 456], 579)

    def test_eval_nested_combination(self):
        self.set_namespace({'add': Procedure(add), 'var': 123})
        self.assert_eval_results(['add', 'var', ['add', 1, 2]], 126)

    def test_eval_special_form(self):
        self.env = Environment(special_forms={'first': first})
        self.assert_eval_results(['first', 'var'], 'var')

    def test_eval_defined_procedure(self):
        self.set_namespace({'add': Procedure(add),
                            'func': Procedure(['add', 'x', 'y'],
                                              parameters=['x', 'y'])})
        self.assert_eval_results(['func', 1, 2], 3)

    def test_eval_nested_defined_procedure(self):
        self.set_namespace({'add': Procedure(add),
                            'func': Procedure(['add', 'x', ['add', 20, 'y']],
                                              parameters=['x', 'y'])})
        self.assert_eval_results(['func', 1, 2], 23)


TRUE_VALUE = 'T'
FALSE_VALUE = 'F'
VAL1 = 'val1'
VAL2 = 'val2'

class test_special_forms(TestCase):

    def setUp(self):
        self.env = Environment()
        self.set_namespace({})

    def set_namespace(self, namespace):
        namespace.update({TRUE_VALUE: True, FALSE_VALUE: False,
                          VAL1: 1, VAL2: 2})
        self.env.namespace = namespace

    def assert_define_sets_namespace(self, inp, name, contents):
        result = self.env._define(inp)
        self.assertEqual(result, None)
        self.assertEqual(self.env.namespace[name], contents)

    # define
    def test_define(self):
        self.assert_define_sets_namespace(['x', 42], 'x', 42)

    def test_define_evals_argument(self):
        self.set_namespace({'add': Procedure(add)})
        self.assert_define_sets_namespace(['x', ['add', 1, 2]], 'x', 3)

    def test_define_compound_procedure1(self):
        self.assert_define_sets_namespace(
            [['x', 'param'], 'param'],
            'x', Procedure('param', parameters=['param']))

    def test_define_compound_procedure2(self):
        self.assert_define_sets_namespace(
            [['f', 'x', 'y', 'z'], ['x', 'y', 'z']],
            'f', Procedure(['x', 'y', 'z'], parameters=['x', 'y', 'z']))

    # cond
    def test_cond_first_predicate_true(self):
        result = self.env._cond([[TRUE_VALUE, VAL1], [FALSE_VALUE, VAL2]])
        self.assertEqual(1, result)

    def test_cond_second_predicate_true(self):
        result = self.env._cond([[FALSE_VALUE, VAL1], [TRUE_VALUE, VAL2]])
        self.assertEqual(2, result)

    def test_cond_no_predicate_true(self):
        # Value of cond is undefined if no predicate evaluates to true
        result = self.env._cond([[FALSE_VALUE, VAL1], [FALSE_VALUE, VAL2]])
        # Don't care about result, just don't crash
        self.assertTrue(True)

    def test_ill_formed_cond_throws_error(self):
        # Only predicate, no consequent expression.  Make sure some
        # kind of exception is raised.
        self.assertRaises(Exception, self.env._cond, ['1'])

    def test_if_true(self):
        self.set_namespace({'predicate': 1, 'yes': 2, 'no': 3})
        result = self.env._if(['predicate', 'yes', 'no'])
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

    def test_greater_than(self):
        result = Builtins.greater_than([4, 3])
        self.assertTrue(result)
        result = Builtins.greater_than([4, 4])
        self.assertFalse(result)

    def test_less_than(self):
        result = Builtins.less_than([3, 4])
        self.assertTrue(result)
        result = Builtins.less_than([4, 4])
        self.assertFalse(result)

    def test_equals(self):
        result = Builtins.equals([3, 3])
        self.assertTrue(result)
        result = Builtins.equals([3, 4])
        self.assertFalse(result)


class test_procedure(TestCase):
    def test_equality_true(self):
        """Test that identical Procedure objects compares to true.

        Procedures are compared for equality in tests that set the
        namespace of the environment, containing procedures."""

        p1 = Procedure(add)
        p2 = Procedure(add)
        p3 = Procedure(['foo', 'a'], parameters=['a'])
        p4 = Procedure(['foo', 'a'], parameters=['a'])
        self.assertEqual(p1, p2)
        self.assertEqual(p3, p4)

    def test_equality_false(self):
        """Test that different Procedure objects compares to false.

        Procedures are compared for equality in tests that set the
        namespace of the environment, containing procedures."""

        p1 = Procedure(add)
        p2 = Procedure(sum)
        p3 = Procedure(['foo', 'a'], parameters=['a'])
        p4 = Procedure(['foo', 'a'])
        p5 = Procedure(['bar', 'a'])
        self.assertNotEqual(p1, p2)
        self.assertNotEqual(p3, p4)
        self.assertNotEqual(p4, p5)

    def test_apply_python_function(self):
        """Test primitive procedure, implemented in Python"""

        p = Procedure(add)
        result = p.apply(None, [1, 2])
        self.assertEqual(result, 3)

    def test_apply_combination(self):
        """Test that a compound procedure is correctly applied."""

        e = Environment(namespace={'f': Procedure(add)})
        p = Procedure(['f', 'x', 'y'], parameters=['x', 'y'])
        result = p.apply(e, [1, 2])
        self.assertEqual(result, 3)

    def test_apply_primitive_body(self):
        """Test procedure with body only consisting of a primitive."""

        e = Environment()
        p = Procedure('x', parameters=['x'])
        result = p.apply(e, [20])
        self.assertEqual(result, 20)


if __name__ == '__main__':
    main()
