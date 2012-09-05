import StringIO
from unittest import TestCase, main
from pysc.parser import Parser, ParseError

class test_parser(TestCase):
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
