from unittest import TestCase, main
from interpreter import Environment, Procedure, Parameter

def add(a, b):
    return a + b

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
                                                 Parameter(0), Parameter(1)])})
        result = env.eval(['func', '1', '2'])
        self.assertEquals(3, result)

    def test_eval_nested_defined_procedure(self):
        env = Environment(namespace={'add': Procedure(add),
                                        'func': Procedure(['add',
                                                 Parameter(0),
                                                 ['add', 20, Parameter(1)]])})
        result = env.eval(['func', '1', '2'])
        self.assertEquals(23, result)


if __name__ == '__main__':
    main()
