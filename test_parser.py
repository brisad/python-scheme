from unittest import TestCase, main
from parser import Parser, ParseError

class test_parser(TestCase):
    def setUp(self):
        self.p = Parser()

    def assert_parse_results(self, inp, outp):
        result = self.p.parse(inp)
        self.assertEqual(outp, list(result))

    def assert_parse_one_result(self, inp, outp):
        result = self.p.parse(inp)
        self.assertEqual(outp, list(result)[0])

    def assert_parse_empty_iterator(self, inp):
        self.assertEqual(0, len(list(self.p.parse(inp))))

    def test_parse_empty_input(self):
        self.assert_parse_empty_iterator('')

    def test_parse_empty_parentheses(self):
        self.assert_parse_empty_iterator('()')

    def test_parse_single_expression(self):
        self.assert_parse_one_result('(+ 1 5)', ['+', '1', '5'])

    def test_parser_nested_expression(self):
        self.assert_parse_one_result('(+ (- 5 4) 3)',
                                     ['+', ['-', '5', '4'], '3'])

    def test_parser_complex_expression(self):
        self.assert_parse_one_result('(+ (/ a b) (* 3 (x y z)))',
                                     ['+', ['/', 'a', 'b'],
                                      ['*', '3', ['x', 'y', 'z']]])

    def test_parser_unmatched_parantheses_throws_error1(self):
        result = self.p.parse('(a ) b)')
        self.assertRaises(ParseError, list, result)

    def test_parser_unmatched_parantheses_throws_error2(self):
        result = self.p.parse('(a ( b)')
        self.assertRaises(ParseError, list, result)

    def test_parser_primitive_expression(self):
        self.assert_parse_one_result('123', '123')

    def test_parser_primitive_float_expression(self):
        self.assert_parse_one_result('3.14', '3.14')

    def test_parser_multiple_expressions(self):
        self.assert_parse_results('10 () (+ 1 2)', ['10', ['+', '1', '2']])


if __name__ == '__main__':
    main()
