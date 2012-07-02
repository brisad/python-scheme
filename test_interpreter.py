from unittest import TestCase, main
from interpreter import Interpreter

def func(a, b):
    return a + b

def func2(x):
    return x[0]

class test_interpreter(TestCase):
    def test_eval_numerical_primitive(self):
        inter = Interpreter()
        result = inter.eval('123')
        self.assertEquals(123, result)

    def test_eval_variable(self):
        inter = Interpreter(namespace={'var': 123})
        result = inter.eval('var')
        self.assertEquals(123, result)

    def test_eval_function(self):
        inter = Interpreter(namespace={'func': func})
        result = inter.eval('func')
        self.assertEquals(func, result)

    def test_eval_combination(self):
        inter = Interpreter(namespace={'func': func, 'var': 123})
        result = inter.eval(['func', 'var', '456'])
        self.assertEquals(579, result)

    def test_eval_nested_combination(self):
        inter = Interpreter(namespace={'func': func, 'var': 123})
        result = inter.eval(['func', 'var', ['func', '1', '2']])
        self.assertEquals(126, result)

    def test_eval_special_form(self):
        inter = Interpreter(special_forms={'func': func2})
        result = inter.eval(['func', 'var'])
        self.assertEquals('var', result)

if __name__ == '__main__':
    main()
