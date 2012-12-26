import sys
import re
import StringIO
from environment import Expression


class ParseError(Exception):
    pass


class Parser(object):
    """Parse character streams into Expressions

    Instances of Parser read input as streams, which are converted
    into Scheme expressions.

    The classmethod from_string() can be used if the input is
    available as a string.
    """

    def __init__(self, stream, output=None, prompt1=None, prompt2=None):
        """Create parser connected to specified stream.

        output -- stream to output prompt on (default None)
        prompt1 -- prompt for each new expression (default None)
        prompt2 -- prompt for unfinished expressions (default None)

        """

        self.push_back = None
        self.stream = stream
        self.output = output
        self.prompt1 = prompt1
        self.prompt2 = prompt2

    def _to_constant(self, primitive):
        """Attempt to convert primitive to constant.

        On success the constant is returned, otherwise a ValueError
        exception is raised.

        """

        if primitive[0] == '"':
            assert primitive[-1] == '"'
            return primitive[1:-1]
        return float(primitive) if '.' in primitive else int(primitive)

    def next_token(self):
        """Return next token from stream as a string.

        At end-of-stream, return None.

        """

        # If there's a character in self.push_back, use it.  Otherwise
        # read the next one from the stream.
        if self.push_back is not None:
            c = self.push_back
            self.push_back = None
        else:
            c = self.stream.read(1)

        # Read up until the first non-whitespace character, but
        # exclude newlines from characters to skip, as they will be
        # returned as tokens.  This is to aid interactive terminals.
        while c.isspace() and c != '\n':
            c = self.stream.read(1)

        # Skip rest of line if a comment is found
        if c == ';':
            while c != '' and c != '\n':
                c = self.stream.read(1)

        # Parentheses and newlines are special, return them
        # immediately if found.
        if c == '(' or c == ')' or c == '\n':
            token = c
        elif c == '"':
            # Start a string constant
            token = '"'
            c = self.stream.read(1)
            while c != '"':
                token += c
                c = self.stream.read(1)
            token += '"'
        else:
            token = ''
            # Build up the token until a whitespace or parenthesis are
            # found
            while not c.isspace() and len(c) > 0 and c != '(' and c != ')':
                token += c
                c = self.stream.read(1)
            # Push next character back so that it will be read at next
            # call
            self.push_back = c

        return token if token != '' else None

    def _get_next_expr(self, prompt):
        """Return next expression from input stream.

        Returns an instance of Expression, or None if end-of-stream is
        encountered.

        If a prompt is passed as argument, output it on output stream
        everytime a newline is encountered in the input.
        """

        token = self.next_token()
        while token == '\n':
            if prompt:
                self.output.write(prompt)
            token = self.next_token()

        if token == '(':
            # Find all subexpressions, continue until we get a
            # ParseError due to a closing parenthesis
            comb = []
            while True:
                try:
                    subexpr = self._get_next_expr(self.prompt2)
                except ParseError:
                    break

                if subexpr is None:
                    # Reached EOF
                    raise ParseError("Unexpected: EOF")
                comb.append(subexpr)
            # Convert list of expressions into an Expression object
            # which is a combination
            expr = Expression(comb, Expression.COMBINATION)

        elif token == ')':
            # A single closing parenthesis is an invalid expression
            raise ParseError("Unexpected: ')'")
        elif token is None:
            expr = None
        else:
            try:
                const = self._to_constant(token)
                expr = Expression(const, Expression.CONSTANT)
            except ValueError:
                expr = Expression(token, Expression.NAME)

        return expr

    def expressions(self):
        """Return all expressions in stream as a generator."""

        expr = self._get_next_expr(self.prompt1)
        while expr is not None:
            yield expr
            expr = self._get_next_expr(self.prompt1)

    @classmethod
    def from_string(cls, string):
        """Return list of expressions parsed from string

        Convenience method to automatically convert the string into a
        stream and create a Parser object to parse the input.
        """

        stream = StringIO.StringIO(string)
        parser = Parser(stream)
        return list(parser.expressions())
