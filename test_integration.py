import os
from itertools import ifilter, imap
from interpreter import Interpreter

def run_test(filename):
    interp = Interpreter()
    num_tests, num_passed = 0, 0
    with open(filename) as f:
        # Iterate over non-blank lines
        for line in ifilter(None, imap(str.strip, f)):
            if line.startswith('> '):
                num_tests += 1
                for response in interp.eval(line[2:]):
                    response = repr(response) if response else ''
                # Got respone, now read next line directly
                expected = next(f).rstrip('\n')
                if response != expected:
                    print 'Failure: "%s" != "%s"' % (response, expected)
                else:
                    num_passed += 1
            else:
                print 'Unexpected line: "%s"' % line
    print "{:20} Ran {} tests, {} passed".format(os.path.basename(filename),
                                                 num_tests, num_passed)


if __name__ == '__main__':
    sessiondir = 'tests/sessions'
    for filename in os.listdir(sessiondir):
        run_test(os.path.join(sessiondir, filename))
