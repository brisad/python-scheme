import sys
import re

class ParseError(Exception):
    pass

class Parser(object):

    def __init__(self, stream=None, output=None, prompt1=None, prompt2=None):
        self.tokenizer = re.compile(r'\(|\)|\+|\-|\*|/|\s*[\w\.]+')
        self.push_back = None
        self.stream = stream
        self.output = output
        self.prompt1 = prompt1
        self.prompt2 = prompt2

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

        # If there's a character in self.push_back, use it.  Otherwise
        # read the next one from the stream.
        if self.push_back is not None:
            c = self.push_back
            self.push_back = None
        else:
            c = stream.read(1)

        # Read up until the first non-whitespace character, but
        # exclude newlines from characters to skip, as they will be
        # returned as tokens.  This is to aid interactive terminals.
        while c.isspace() and c != '\n':
            c = stream.read(1)

        # Parentheses and newlines are special, return them
        # immediately if found.
        if c == '(' or c == ')' or c == '\n':
            token = c
        else:
            token = ''
            # Build up the token until a whitespace or parenthesis are
            # found
            while not c.isspace() and len(c) > 0 and c != '(' and c != ')':
                token += c
                c = stream.read(1)
            # Push next character back so that it will be read at next
            # call
            self.push_back = c

        token = self._convert(token)
        return token if token != '' else None

    def _get_next_expr(self, prompt):
        """Return next expression from input stream.

        If set, output prompt on output stream everytime a newline is
        encountered in the input."""

        expr = []
        token = self.next_token(self.stream)
        while token == '\n':
            if prompt:
                self.output.write(prompt)
            token = self.next_token(self.stream)

        if token == '(':
            # Find all subexpressions, continue until we get a
            # ParseError due to a closing parenthesis
            while True:
                try:
                    subexpr = self._get_next_expr(self.prompt2)
                except ParseError:
                    break

                if subexpr is None:
                    # Reached EOF
                    raise ParseError("Unexpected: EOF")
                expr.append(subexpr)

        elif token == ')':
            # A single closing parenthesis is an invalid expression
            raise ParseError("Unexpected: ')'")
        else:
            expr = token

        return expr

    def expressions(self):
        """Return all expressions in stream as generator."""

        expr = self._get_next_expr(self.prompt1)
        while expr is not None:
            yield expr
            expr = self._get_next_expr(self.prompt1)
