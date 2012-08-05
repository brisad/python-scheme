import re

class ParseError(Exception):
    pass

class Parser(object):

    def __init__(self):
        self.tokenizer = re.compile(r'\(|\)|\+|\-|\*|/|\s*[\w\.]+')
        self.push_back = None

    def _convert(self, primitive):
        try:
            return float(primitive) if '.' in primitive else int(primitive)
        except ValueError:
            return primitive

    def _recurse(self, tokens):

        result = []
        for token in tokens:
            if token == '(':
                token = self._recurse(tokens)
            elif token == ')':
                break
            else:
                token = self._convert(token)

            result.append(token)
        else:
            raise ParseError("Expected: ')'")

        return result

    def parse(self, string):
        # Tokenize input and remove any spaces in the tokens
        tokens = (x.strip() for x in self.tokenizer.findall(string))

        for first in tokens:
            if first == ')':
                raise ParseError("Unexpected: ')'")
            elif first == '(':

                result = self._recurse(tokens)
                if not result:
                    continue
            else: # Not '(', ')'
                # Not a combination, yield primitive expression
                result = self._convert(first)

            yield result

    def next_token(self, stream):
        """Return next token from stream."""

        if self.push_back is not None:
            result = self.push_back
            self.push_back = None
            return result

        # Read up until first non-whitespace character
        c = stream.read(1)
        while c.isspace():
            c = stream.read(1)

        # Parentheses are special, return them immediately if found
        if c == '(' or c == ')':
            token = c
        else:
            token = ''
            # Build up the token until a whitespace or parenthesis are
            # found
            while not c.isspace() and len(c) > 0 and c != '(' and c != ')':
                token += c
                c = stream.read(1)
            # If we found a parenthesis, push it back so that it will
            # be read at next call
            if c == '(' or c == ')':
                self.push_back = c

        token = self._convert(token)
        return token if token != '' else None

    def next_expr(self, stream):
        """Return next expression from stream."""

        expr = []
        token = self.next_token(stream)
        if token == '(':
            # Find all subexpressions, continue until we get a
            # ParseError due to a closing parenthesis
            while True:
                try:
                    subexpr = self.next_expr(stream)
                except ParseError:
                    break
                expr.append(subexpr)

        elif token == ')':
            # A single closing parenthesis is an invalid expression
            raise ParseError("Unexpected: ')'")
        else:
            expr = token

        return expr
