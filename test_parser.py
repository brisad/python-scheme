from unittest import TestCase, main
from parser import Parser, ParseError

class test_parser(TestCase):
    def setUp(self):
        self.p = Parser()

    def assert_parse_results(self, inp, outp):
        result = self.p.parse(inp)
        self.assertEquals(outp, result)

    def test_parse_empty_input(self):
        self.assert_parse_results('', None)

    def test_parse_empty_parentheses(self):
        self.assert_parse_results('()', None)

    def test_parse_single_expression(self):
        self.assert_parse_results('(+ 1 5)', ['+', '1', '5'])

    def test_parser_nested_expression(self):
        self.assert_parse_results('(+ (- 5 4) 3)', ['+', ['-', '5', '4'], '3'])

    def test_parser_complex_expression(self):
        self.assert_parse_results('(+ (/ a b) (* 3 (x y z)))',
                            ['+', ['/', 'a', 'b'], ['*', '3', ['x', 'y', 'z']]])

    def test_parser_unmatched_parantheses_throws_error1(self):
        self.assertRaises(ParseError, self.p.parse, '(a ) b)')

    def test_parser_unmatched_parantheses_throws_error2(self):
        self.assertRaises(ParseError, self.p.parse, '(a ( b)')


if __name__ == '__main__':
    main()