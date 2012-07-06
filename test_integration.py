import os
from interpreter import Interpreter

def run_test(filename):
    interp = Interpreter()
    response = None
    num_tests = 0
    with open(filename) as f:
        for line in f:
            if response:
                assert response == line.rstrip('\n')
                response = None
            elif line.startswith('> '):
                num_tests += 1
                for response in interp.eval(line[2:]):
                    response = str(response)
    print "{:20} Ran {} tests successfully".format(os.path.basename(filename),
                                                    num_tests)

if __name__ == '__main__':
    sessiondir = 'tests/sessions'
    for filename in os.listdir(sessiondir):
        run_test(os.path.join(sessiondir, filename))
