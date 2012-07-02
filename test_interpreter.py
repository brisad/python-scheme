from unittest import TestCase, main
from interpreter import Interpreter

def func(a, b):
    return a + b

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


if __name__ == '__main__':
    main()
