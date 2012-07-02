import re

class ParseError(Exception):
    pass

class Parser(object):

    def _recurse(self, fields):

        result = []
        for field in fields:
            if field == '(':
                field = self._recurse(fields)
            if field == ')':
                break
            result.append(field)
        else:
            raise ParseError("Expected: ')'")

        return result

    def parse(self, string):

        fields = iter(re.findall(r'\(|\)|\b[^\W]+\b|\+|\-|\/|\*', string))

        for first in fields:
            if first == ')':
                raise ParseError("Unexpected: ')'")
            elif first == '(':

                result = self._recurse(fields)
                if not result:
                    continue
            else: # Not '(', ')'
                # Not a combination, yield primitive expression
                result = first

            yield result
