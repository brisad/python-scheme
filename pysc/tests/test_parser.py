import StringIO
from unittest import TestCase, main
from pysc.parser import Parser, ParseError

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

    def list_expressions(self, inp):
        stream = StringIO.StringIO(inp)
        self.p = Parser(stream)
        result = self.p.expressions()
        return list(result)

    def assert_expressions_results(self, inp, outp):
        self.assertEqual(outp, self.list_expressions(inp)[0])

    def assert_expressions_results_all(self, inp, outp):
        self.assertEqual(outp, self.list_expressions(inp))

    def assert_expressions_none(self, inp):
        self.assertEqual(0, len(self.list_expressions(inp)))

    def assert_expressions_throws(self, inp, error):
        self.assertRaises(error, self.list_expressions, inp)

    def test_expressions_empty(self):
        self.assert_expressions_none('')

    def test_expressions_symbol(self):
        self.assert_expressions_results('symbol', 'symbol')

    def test_expressions_symbol_with_whitespace(self):
        self.assert_expressions_results(' symbol ', 'symbol')

    def test_expressions_integer(self):
        self.assert_expressions_results('42', 42)

    def test_expressions_zero(self):
        self.assert_expressions_results('0', 0)

    def test_expressions_float(self):
        self.assert_expressions_results('3.14', 3.14)

    def test_expressions_combination(self):
        self.assert_expressions_results('(symbol 42 3.14)', ['symbol', 42, 3.14])

    def test_expressions_nested_combination(self):
        self.assert_expressions_results('(symbol (42 (3.14) 0))',
                                      ['symbol', [42, [3.14], 0]])

    def test_expressions_complex(self):
        self.assert_expressions_results('(a-b - + a+b .( a  b c)(.9 o/ /))',
                                      ['a-b', '-', '+', 'a+b', '.',
                                       ['a', 'b', 'c'], [.9, 'o/', '/']])

    def test_expressions_multiple(self):
        self.assert_expressions_results_all('(a) b (c)', [['a'], 'b', ['c']])

    def test_expressions_unmatched_parantheses_throws_error(self):
        self.assert_expressions_throws(')', ParseError)

    def test_expressions_uncomplete_throws_error(self):
        self.assert_expressions_throws('(+ 1', ParseError)
 
    def test_expressions_interactive_shows_prompt(self):
        stream = StringIO.StringIO('\n')
        outstream = StringIO.StringIO()
        self.p = Parser(stream, outstream, '> ')
        list(self.p.expressions())
        outstream.seek(0)
        self.assertEqual('> ', outstream.read())

    def test_expressions_interactive_shows_secondary_prompt(self):
        stream = StringIO.StringIO('(\n)')
        outstream = StringIO.StringIO()
        self.p = Parser(stream, outstream, '> ', '. ')
        list(self.p.expressions())
        outstream.seek(0)
        self.assertEqual('. ', outstream.read())


if __name__ == '__main__':
    main()
