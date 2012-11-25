import os
import StringIO
from itertools import ifilter, imap
from pysc.environment import Environment, Builtins, Expression
from pysc.parser import Parser


def run_session(filename):
    """Run session test.

    Output summary to stdout and return True if all test pass,
    otherwise return False."""

    env = Environment(namespace=Builtins.namespace())
    num_tests, num_passed = 0, 0
    with open(filename) as f:
        input_expression = ""
        # Iterate over non-blank lines
        for line in ifilter(None, imap(str.strip, f)):
            if line.startswith('> '):
                # Lines are stripped, so add a space to get whitespace
                # between the lines.
                input_expression += " " + line[2:]
            elif input_expression:
                # We got a line not starting with '> ', this is the
                # expected result from the preceding input expression
                num_tests += 1

                parser = Parser(StringIO.StringIO(input_expression))
                for expr in parser.expressions():
                    result = env.eval(expr)
                    result = repr(result) if result is not None else ''

                expected = line.rstrip('\n')
                if result != expected:
                    print 'Failure: "%s" != "%s"' % (result, expected)
                else:
                    num_passed += 1
                input_expression = ""
            else:
                # If we got a non-empty line without an input
                # expression something is wrong
                print 'Unexpected line: "%s"' % line
    print "{:20} Ran {} tests, {} passed".format(os.path.basename(filename),
                                                 num_tests, num_passed)
    return num_tests == num_passed

def test_all_sessions(assert_success=True):
    """Test all session files.

    If assert_success is true, for each run test, assert it's success.
    Then if there is a failure the remaining tests will not run.  This
    is to be used when nose runs the tests.

    When runnning standalone it should be called with assert_success
    set to False in order to see a summary of the results of all
    session tests."""

    sessiondir = os.path.join(os.path.dirname(__file__), 'sessions')
    entries = [os.path.join(sessiondir, x) for x in os.listdir(sessiondir)]
    for filename in ifilter(os.path.isfile, entries):
        success = run_session(filename)
        if assert_success:
            assert success


if __name__ == '__main__':
    test_all_sessions(assert_success=False)
