import re

class ParseError(Exception):
    pass

class Parser(object):

    def __init__(self):
        self.tokenizer = re.compile(r'\(|\)|\+|\-|\*|/|\s*[\w\.]+')

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
