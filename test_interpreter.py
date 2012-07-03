from unittest import TestCase, main
from interpreter import Interpreter, Procedure, Parameter

def add(a, b):
    return a + b

def first(x):
    return x[0]

class test_interpreter(TestCase):
    def test_eval_numerical_primitive(self):
        interp = Interpreter()
        result = interp.eval('123')
        self.assertEquals(123, result)

    def test_eval_variable(self):
        interp = Interpreter(namespace={'var': 123})
        result = interp.eval('var')
        self.assertEquals(123, result)

    def test_eval_function(self):
        interp = Interpreter(namespace={'add': add})
        result = interp.eval('add')
        self.assertEquals(add, result)

    def test_eval_combination(self):
        interp = Interpreter(namespace={'add': Procedure(add), 'var': 123})
        result = interp.eval(['add', 'var', '456'])
        self.assertEquals(579, result)

    def test_eval_nested_combination(self):
        interp = Interpreter(namespace={'add': Procedure(add), 'var': 123})
        result = interp.eval(['add', 'var', ['add', '1', '2']])
        self.assertEquals(126, result)

    def test_eval_special_form(self):
        interp = Interpreter(special_forms={'first': first})
        result = interp.eval(['first', 'var'])
        self.assertEquals('var', result)

    def test_eval_defined_procedure(self):
        interp = Interpreter(namespace={'add': Procedure(add),
                                        'func': Procedure(['add',
                                                 Parameter(0), Parameter(1)])})
        result = interp.eval(['func', '1', '2'])
        self.assertEquals(3, result)

    def test_eval_nested_defined_procedure(self):
        interp = Interpreter(namespace={'add': Procedure(add),
                                        'func': Procedure(['add',
                                                 Parameter(0),
                                                 ['add', 20, Parameter(1)]])})
        result = interp.eval(['func', '1', '2'])
        self.assertEquals(23, result)


if __name__ == '__main__':
    main()
