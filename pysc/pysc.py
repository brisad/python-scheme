import sys
from parser import Parser
from environment import Environment, Builtins, Expression

class Interpreter(object):
    def __init__(self, instream=sys.stdin, outstream=sys.stdout,
                 prompt1='> ', prompt2=None):
        self.instream = instream
        self.outstream = outstream
        self.prompt1 = prompt1
        self.prompt2 = prompt2
        self.parser = Parser(self.instream, self.outstream,
                             self.prompt1, self.prompt2)
        self.environment = Environment(namespace=Builtins.namespace())

    def run(self):
        self.outstream.write(self.prompt1)
        try:
            for expr in self.parser.expressions():
                print self.environment.eval(Expression.create(expr))
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    Interpreter().run()
