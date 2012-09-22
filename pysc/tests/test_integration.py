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
        # Iterate over non-blank lines
        for line in ifilter(None, imap(str.strip, f)):
            if line.startswith('> '):
                num_tests += 1

                for expr in Parser(StringIO.StringIO(line[2:])).expressions():
                    result = env.eval(Expression.create(expr))
                    result = repr(result) if result else ''

                # Got respone, now read next line directly
                expected = next(f).rstrip('\n')
                if result != expected:
                    print 'Failure: "%s" != "%s"' % (result, expected)
                else:
                    num_passed += 1
            else:
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
    for filename in os.listdir(sessiondir):
        success = run_session(os.path.join(sessiondir, filename))
        if assert_success:
            assert success


if __name__ == '__main__':
    test_all_sessions(assert_success=False)
