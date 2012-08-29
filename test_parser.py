import StringIO
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

    def test_parser_primitive_expression(self):
        self.assert_parse_one_result('123', 123)

    def test_parser_primitive_float_expression(self):
        self.assert_parse_one_result('3.14', 3.14)

    def test_parse_combination(self):
        self.assert_parse_one_result('(+ 1 2.1)', ['+', 1, 2.1])

    def test_parser_nested_combination(self):
        self.assert_parse_one_result('(+ (- 5 4) (u 0.5 a))',
                                     ['+', ['-', 5, 4], ['u', 0.5, 'a']])

    def test_parser_multiple_expressions(self):
        self.assert_parse_results('10 () (+ 1 2)', [10, ['+', 1, 2]])

    def test_parser_unmatched_parantheses_throws_error1(self):
        result = self.p.parse('(a ) b)')
        self.assertRaises(ParseError, list, result)

    def test_parser_unmatched_parantheses_throws_error2(self):
        result = self.p.parse('(a ( b)')
        self.assertRaises(ParseError, list, result)

##

    def list_next_expr(self, inp):
        stream = StringIO.StringIO(inp)
        result = self.p.next_expr(stream)
        return list(result)

    def assert_next_expr_results(self, inp, outp):
        self.assertEqual(outp, self.list_next_expr(inp)[0])

    def assert_next_expr_results_all(self, inp, outp):
        self.assertEqual(outp, self.list_next_expr(inp))

    def assert_next_expr_none(self, inp):
        self.assertEqual(0, len(self.list_next_expr(inp)))

    def assert_next_expr_throws(self, inp, error):
        self.assertRaises(error, self.list_next_expr, inp)

    def test_next_expr_empty(self):
        self.assert_next_expr_none('')

    def test_next_expr_symbol(self):
        self.assert_next_expr_results('symbol', 'symbol')

    def test_next_expr_symbol_with_whitespace(self):
        self.assert_next_expr_results(' symbol ', 'symbol')

    def test_next_expr_integer(self):
        self.assert_next_expr_results('42', 42)

    def test_next_expr_zero(self):
        self.assert_next_expr_results('0', 0)

    def test_next_expr_float(self):
        self.assert_next_expr_results('3.14', 3.14)

    def test_next_expr_combination(self):
        self.assert_next_expr_results('(symbol 42 3.14)', ['symbol', 42, 3.14])

    def test_next_expr_nested_combination(self):
        self.assert_next_expr_results('(symbol (42 (3.14) 0))',
                                      ['symbol', [42, [3.14], 0]])

    def test_next_expr_complex(self):
        self.assert_next_expr_results('(a-b - + a+b .( a  b c)(.9 o/ /))',
                                      ['a-b', '-', '+', 'a+b', '.',
                                       ['a', 'b', 'c'], [.9, 'o/', '/']])

    def test_next_expr_multiple(self):
        self.assert_next_expr_results_all('(a) b (c)', [['a'], 'b', ['c']])

    def test_next_expr_unmatched_parantheses_throws_error(self):
        self.assert_next_expr_throws(')', ParseError)

    def test_next_expr_uncomplete_throws_error(self):
        self.assert_next_expr_throws('(+ 1', ParseError)
 
    def test_next_expr_interactive_shows_prompt(self):
        stream = StringIO.StringIO('\n')
        outstream = StringIO.StringIO()
        list(self.p.next_expr(stream, outp=outstream, prompt='> '))
        outstream.seek(0)
        self.assertEqual('> ', outstream.read())


if __name__ == '__main__':
    main()
