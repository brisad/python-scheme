class Interpreter(object):
    def __init__(self, namespace={}):
        self.namespace = namespace

    def eval(self, expression):
        try:
            result = int(expression)
        except ValueError:
            result = self.namespace.get(expression)

        return result
