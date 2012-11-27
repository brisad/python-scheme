python-scheme
=============

Python-scheme is a Scheme language interpreter implemented in Python. It is currently a work in progress, and the main purpose of it is for me to learn Scheme, while at the same time get a chance to practice Test Driven Development (TDD).

I do this by reading *Structure and Interpretation of Computer Programs (SICP)* by Harold Abelson and Gerald Jay Sussman, and at the same time write tests and implement Scheme language features as I encounter them in the book.

Usage
-----
To start the interactive interpreter, change into the project directory and run

    python pysc/pysc.py

Tests
-----

The python-scheme/tests/ directory contains both unit tests and integration tests. They can all be run by simply running

    nosetests

from the project directory.

The integration tests are run with a simple script test_integration.py, which has similarities to the format used in Python's doctest. To run it separately without nosetest, run it directly from the python-scheme directory so that all modules are loaded correctly:

    python pysc/test/test_integration.py

This will show some output indicating the number of tests run per file, and how many of them that passed, which will not be seen if running through nosetest.

Sessions
--------

The integration tests are stored as session files in tests/sessions and mainly consists of code that are used as examples in SICP. This is to ensure that the interpreter will work as expected as I read through the book.