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
            raise ParseError("Expected ')'")

        return result

    def parse(self, string):

        if not string:
            return None

        fields = iter(re.findall(r'\(|\)|\b[^\W]+\b|\+|\-|\/|\*', string))

        # Check for a primitive expression
        first = fields.next()
        if first != '(':
            # Not a combination
            return first

        result = self._recurse(fields)

        try:
            trailing = fields.next()
        except StopIteration:
            pass
        else:
            if trailing != '(':
                raise ParseError('Trailing data: %s' % trailing)

        if not result:
            return None

        return result
