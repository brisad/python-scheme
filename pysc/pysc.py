import sys
from parser import Parser
from environment import Environment, Builtins, Expression

class Interpreter(object):

    """This class holds references to input and output streams and
    their prompts and uses them for running a line based interpreter.

    Public methods:
    run() -- Run interpreter by evaluating expressions
    """

    def __init__(self, instream=sys.stdin, outstream=sys.stdout,
                 prompt1=None, prompt2=None):
        """Create Interpreter object.

        Prepare interpreter for running by specifying the streams to
        use and prompts if any.

        prompt1 is the prompt that is shown before a line, indicating
        that the interpreter is ready to process a new expression.
        prompt2 is the secondary prompt, which appears for each new
        line in input only when the interpreter is awaiting more input
        that is needed to finish reading a complete expression.

        Normally prompts are only used in interactive sessions, and
        prompt1 will only get it's default value when both instream
        and outstream return True for isatty().  This can be
        overridden by just specifying a prompt explicitly.

        Keyword arguments:
        instream -- stream to read input from (default sys.stdin)
        outstream -- stream to write output to (default sys.stdout)
        prompt1 -- Normal prompt (default '> ' if interactive)
        prompt2 -- Secondary prompt (default None)
        """

        self.instream = instream
        self.outstream = outstream

        if prompt1 is None and instream.isatty() and outstream.isatty():
            prompt1 = '> '
        self.prompt1 = prompt1
        self.prompt2 = prompt2
        self.parser = Parser(self.instream, self.outstream,
                             self.prompt1, self.prompt2)
        self.environment = Environment(namespace=Builtins.namespace())

    def run(self):
        """Run interpreter by evaluating expessions.

        Parses input stream and returns expressions which then are
        evaluated by the environment.  The results are then written,
        for each evaluated expression, to the output stream.
        """

        if self.prompt1:
            self.outstream.write(self.prompt1)
        try:
            for expr in self.parser.expressions():
                print self.environment.eval(Expression.create(expr))
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    if len(sys.argv) > 1:
        for file_ in sys.argv[1:]:
            with open(file_, 'r') as f:
                Interpreter(f).run()
    else:
        Interpreter().run()
