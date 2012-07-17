from unittest import TestCase, main
from mocker import Mocker
from interpreter import Environment, Procedure, Builtins

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

    def assert_define_sets_namespace(self, inp, name, contents):
        result = self.env._define(inp)
        self.assertEqual(result, None)
        self.assertEqual(self.env.namespace[name], contents)

    def test_eval_numerical_primitive(self):
        self.assert_eval_results('123', 123)

    def test_eval_numerical_float_primitive(self):
        self.assert_eval_results('3.14', 3.14)

    def test_eval_variable(self):
        self.set_namespace({'var': 123})
        self.assert_eval_results('var', 123)

    def test_eval_function(self):
        self.set_namespace({'add': add})
        self.assert_eval_results('add', add)

    def test_eval_combination(self):
        self.set_namespace({'add': Procedure(add), 'var': 123})
        self.assert_eval_results(['add', 'var', '456'], 579)

    def test_eval_nested_combination(self):
        self.set_namespace({'add': Procedure(add), 'var': 123})
        self.assert_eval_results(['add', 'var', ['add', '1', '2']], 126)

    def test_eval_special_form(self):
        self.env = Environment(special_forms={'first': first})
        self.assert_eval_results(['first', 'var'], 'var')

    def test_eval_defined_procedure(self):
        self.set_namespace({'add': Procedure(add),
                            'func': Procedure(['add', 'x', 'y'],
                                              parameters=['x', 'y'])})
        self.assert_eval_results(['func', '1', '2'], 3)

    def test_eval_nested_defined_procedure(self):
        self.set_namespace({'add': Procedure(add),
                            'func': Procedure(['add', 'x', ['add', 20, 'y']],
                                              parameters=['x', 'y'])})
        self.assert_eval_results(['func', '1', '2'], 23)

    def test_define(self):
        self.assert_define_sets_namespace(['x', 42], 'x', 42)

    def test_define_parameters1(self):
        self.assert_define_sets_namespace(
            [['x', 'param'], 'param'],
            'x', Procedure('param', parameters=['param']))

    def test_define_parameters2(self):
        self.assert_define_sets_namespace(
            [['f', 'x', 'y', 'z'], ['x', 'y', 'z']],
            'f', Procedure(['x', 'y', 'z'], parameters=['x', 'y', 'z']))

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


class test_procedure(TestCase):
    def test_equality_true(self):
        p1 = Procedure(add)
        p2 = Procedure(add)
        p3 = Procedure(['foo', 'a'], parameters=['a'])
        p4 = Procedure(['foo', 'a'], parameters=['a'])
        self.assertEqual(p1, p2)
        self.assertEqual(p3, p4)

    def test_equality_false(self):
        p1 = Procedure(add)
        p2 = Procedure(sum)
        p3 = Procedure(['foo', 'a'], parameters=['a'])
        p4 = Procedure(['foo', 'a'])
        p5 = Procedure(['bar', 'a'])
        self.assertNotEqual(p1, p2)
        self.assertNotEqual(p3, p4)
        self.assertNotEqual(p4, p5)

    def test_apply_python_function(self):
        p = Procedure(add)
        result = p.apply(None, [1, 2])
        self.assertEquals(result, 3)

    def test_apply_combination(self):
        e = Environment(namespace={'f': Procedure(add)})
        p = Procedure(['f', 'x', 'y'], parameters=['x', 'y'])
        result = p.apply(e, [1, 2])
        self.assertEquals(result, 3)

    def test_apply_primitive_body(self):
        e = Environment()
        p = Procedure('x', parameters=['x'])
        result = p.apply(e, [20])
        self.assertEquals(result, 20)


if __name__ == '__main__':
    main()
