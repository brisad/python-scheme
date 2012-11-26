from unittest import TestCase, main
from pysc.environment import Environment, Procedure, BuiltinProcedure, \
    Expression, Builtins, SymbolError


# Some aliases to greatly reduce space in tests
E = Expression
C = E.COMBINATION
CT = E.CONSTANT
N = E.NAME

# Note: Be sure that no tests modify these Expression objects.
INT_VAL = 123
INT_VAL_EXPR = E(INT_VAL, CT)
FLOAT_VAL = 3.14
FLOAT_VAL_EXPR = E(FLOAT_VAL, CT)
VAL1 = 'val1'
VAL1_EXPR = E(VAL1, N)
VAL2 = 'val2'
VAL2_EXPR = E(VAL2, N)

NUMERIC_VAL = FLOAT_VAL
NUMERIC_VAL_EXPR = E(NUMERIC_VAL, CT)

STRING_VAL = "Hello"

TRUE_VALUE = 'T'
TRUE_VALUE_EXPR = E(TRUE_VALUE, N)
FALSE_VALUE = 'F'
FALSE_VALUE_EXPR = E(FALSE_VALUE, N)
ELSE_EXPR = E('else', N)

DEF_NAME = 'foo'
DEF_NAME_EXPR = E(DEF_NAME, N)
SPEC_FORM_NAME = 'proc'
SPEC_FORM_NAME_EXPR = E(SPEC_FORM_NAME, N)
PROC_NAME = 'proc'
PROC_NAME_EXPR = E(PROC_NAME, N)
PM1 = 'x'
PM1_EXPR = E(PM1, N)
PM2 = 'y'
PM2_EXPR = E(PM2, N)
PM3 = 'z'
PM3_EXPR = E(PM3, N)

ADD = 'add'
ADD_EXPR = E(ADD, N)


def add(operands):
    return operands[0] + operands[1]


class test_environment(TestCase):
    def setUp(self):
        self.env = Environment()

    def set_namespace(self, namespace):
        self.env.namespace = namespace

    def assert_eval_results(self, inp, outp):
        result = self.env.eval(inp)
        self.assertEqual(outp, result)

    def test_eval_numerical_primitive(self):
        self.assert_eval_results(INT_VAL_EXPR, INT_VAL)

    def test_eval_numerical_float_primitive(self):
        self.assert_eval_results(FLOAT_VAL_EXPR, FLOAT_VAL)

    def test_eval_variable(self):
        self.set_namespace({VAL1: NUMERIC_VAL})
        self.assert_eval_results(VAL1_EXPR, NUMERIC_VAL)

    def test_eval_function(self):
        self.set_namespace({ADD: add})
        self.assert_eval_results(ADD_EXPR, add)

    def test_eval_combination(self):
        self.set_namespace({ADD: BuiltinProcedure(add), VAL1: 123})
        self.assert_eval_results(E([ADD_EXPR, VAL1_EXPR, E(456, CT)], C),
                                 579)

    def test_eval_nested_combination(self):
        self.set_namespace({ADD: BuiltinProcedure(add), VAL1: 123})
        self.assert_eval_results(E([ADD_EXPR, VAL1_EXPR,
                                    E([ADD_EXPR, E(1, CT), E(2, CT)], C)], C),
                                 126)

    def test_eval_special_form(self):
        self.env = Environment(special_forms={SPEC_FORM_NAME: lambda x: x[0]})
        self.assert_eval_results(E([SPEC_FORM_NAME_EXPR, PM1_EXPR], C),
                                 PM1_EXPR)

    def test_eval_defined_procedure(self):
        self.set_namespace({ADD: BuiltinProcedure(add),
                            PROC_NAME: Procedure(
                    [E([ADD_EXPR, PM1_EXPR, PM2_EXPR], C)],
                    parameters=[PM1, PM2])})
        self.assert_eval_results(E([PROC_NAME_EXPR, E(1, CT), E(2, CT)], C),
                                 3)

    def test_eval_nested_defined_procedure(self):
        self.set_namespace({ADD: BuiltinProcedure(add),
                            PROC_NAME: Procedure(
                    [E([ADD_EXPR, PM1_EXPR,
                        E([ADD_EXPR, E(20, CT), PM2_EXPR], C)], C)],
                    parameters=[PM1, PM2])})
        self.assert_eval_results(E([PROC_NAME_EXPR, E(1, CT), E(2, CT)], C),
                                 23)

    def test_eval_symbol_not_found_raises_error(self):
        self.assertRaises(SymbolError, self.env.eval, E('foo'))


class test_expression(TestCase):
    def test_scalar(self):
        expr = Expression(NUMERIC_VAL)
        self.assertFalse(expr.is_combination())
        self.assertTrue(expr.is_name())
        self.assertEqual(NUMERIC_VAL, expr.scalar)

    def test_scalar_string(self):
        expr = Expression(STRING_VAL)
        self.assertFalse(expr.is_combination())
        self.assertEqual(STRING_VAL, expr.scalar)

    def test_name(self):
        expr = Expression(STRING_VAL, Expression.NAME)
        self.assertTrue(expr.is_name())
        self.assertFalse(expr.is_combination())
        self.assertEqual(STRING_VAL, expr.scalar)

    def test_constant(self):
        expr = Expression(NUMERIC_VAL, Expression.CONSTANT)
        self.assertTrue(expr.is_constant())
        self.assertFalse(expr.is_name())
        self.assertFalse(expr.is_combination())
        self.assertEqual(NUMERIC_VAL, expr.scalar)

    def test_combination(self):
        expr = Expression([Expression(NUMERIC_VAL),
                           Expression(STRING_VAL)],
                          Expression.COMBINATION)
        self.assertTrue(expr.is_combination())
        self.assertEqual([Expression(NUMERIC_VAL), Expression(STRING_VAL)],
                         expr.fields)

    def test_combination_one_field(self):
        expr = Expression([Expression(NUMERIC_VAL)],
                          Expression.COMBINATION)
        self.assertTrue(expr.is_combination())
        self.assertEqual([Expression(NUMERIC_VAL)], expr.fields)

    def test_scalar_wrong_type_raises_attribute_error(self):
        expr = Expression([NUMERIC_VAL_EXPR], Expression.COMBINATION)
        with self.assertRaises(AttributeError):
            expr.scalar

    def test_fields_wrong_type_raises_attribute_error(self):
        expr = Expression(NUMERIC_VAL, Expression.CONSTANT)
        with self.assertRaises(AttributeError):
            expr.fields

    def test_equality(self):
        """Test __eq__ and __ne__ of Expression."""

        expr1 = Expression([NUMERIC_VAL, STRING_VAL])
        expr2 = Expression([NUMERIC_VAL])
        expr3 = Expression([NUMERIC_VAL, STRING_VAL])
        expr4 = Expression(NUMERIC_VAL)
        expr5 = Expression(NUMERIC_VAL)
        expr6 = Expression([Expression(NUMERIC_VAL)])
        expr7 = Expression(NUMERIC_VAL, Expression.CONSTANT)
        self.assertFalse(expr1 == expr2)
        self.assertTrue(expr1 == expr3)
        self.assertFalse(expr2 == expr4)
        self.assertTrue(expr4 == expr5)
        self.assertFalse(expr2 == expr6)
        self.assertFalse(expr4 == expr7)
        self.assertTrue(expr1 != expr2)
        self.assertFalse(expr1 != expr3)
        self.assertTrue(expr2 != expr4)
        self.assertFalse(expr4 != expr5)
        self.assertTrue(expr2 != expr6)
        self.assertTrue(expr4 != expr7)

    def test_repr_constant(self):
        expr = Expression(INT_VAL, Expression.CONSTANT)
        self.assertEqual('Expression(%s, CONSTANT)' % repr(INT_VAL), repr(expr))

    def test_repr_name(self):
        expr = Expression(STRING_VAL, Expression.NAME)
        self.assertEqual('Expression(%s, NAME)' % repr(STRING_VAL), repr(expr))

    def test_repr_combination(self):
        expr = Expression([INT_VAL_EXPR], Expression.COMBINATION)
        self.assertEqual('Expression(%s, COMBINATION)' % \
                             repr([INT_VAL_EXPR]), repr(expr))

    def test_str_constant(self):
        expr = Expression(INT_VAL, Expression.CONSTANT)
        self.assertEqual('%r' % INT_VAL, str(expr))

    def test_str_name(self):
        expr = Expression(DEF_NAME, Expression.NAME)
        self.assertEqual('%r' % DEF_NAME, str(expr))

    def test_str_combination(self):
        expr = Expression([INT_VAL_EXPR], Expression.COMBINATION)
        self.assertEqual('[%s]' % str(INT_VAL_EXPR), str(expr))


class test_special_forms(TestCase):

    def setUp(self):
        self.env = Environment()
        self.set_namespace({})

    def set_namespace(self, namespace):
        namespace.update({TRUE_VALUE: True, FALSE_VALUE: False,
                          VAL1: 1, VAL2: 2})
        self.env.namespace = namespace

    def call_special_form(self, special_form, inp):
        result = special_form(inp)
        return result

    def assert_special_form_returns(self, special_form, inp, outp):
        result = self.call_special_form(special_form, inp)
        self.assertEqual(outp, result)

    def assert_define_sets_namespace(self, inp, name, contents):
        result = self.call_special_form(self.env._define, inp)
        self.assertEqual(result, name)
        self.assertEqual(self.env.namespace[name], contents)

    # define
    def test_define(self):
        self.assert_define_sets_namespace(
            [DEF_NAME_EXPR, NUMERIC_VAL_EXPR],
            DEF_NAME,
            NUMERIC_VAL)

    def test_define_evals_argument(self):
        self.set_namespace({ADD: BuiltinProcedure(add)})
        self.assert_define_sets_namespace(
            [DEF_NAME_EXPR,
             E([ADD_EXPR, NUMERIC_VAL_EXPR, NUMERIC_VAL_EXPR], C)],
            DEF_NAME,
            2 * NUMERIC_VAL)

    def test_define_compound_procedure1(self):
        self.assert_define_sets_namespace(
            [E([PROC_NAME_EXPR, PM1_EXPR], C), PM1_EXPR],
            PROC_NAME,
            Procedure([PM1_EXPR], parameters=[PM1]))

    def test_define_compound_procedure2(self):
        self.assert_define_sets_namespace(
            [E([PROC_NAME_EXPR, PM1_EXPR, PM2_EXPR, PM3_EXPR], C),
             E([PM1_EXPR, PM2_EXPR, PM3_EXPR], C)],
            PROC_NAME,
            Procedure([E([PM1_EXPR, PM2_EXPR, PM3_EXPR], C)],
                      parameters=[PM1, PM2, PM3]))

    # cond
    def test_cond_first_predicate_true(self):
        self.assert_special_form_returns(
            self.env._cond,
            [E([TRUE_VALUE_EXPR, VAL1_EXPR], C),
             E([FALSE_VALUE_EXPR, VAL2_EXPR], C)],
            1)

    def test_cond_second_predicate_true(self):
        self.assert_special_form_returns(
            self.env._cond,
            [E([FALSE_VALUE_EXPR, VAL1_EXPR], C),
             E([TRUE_VALUE_EXPR, VAL2_EXPR], C)],
            2)

    def test_cond_no_predicate_true(self):
        # Value of cond is undefined if no predicate evaluates to true
        self.call_special_form(
            self.env._cond,
            [E([FALSE_VALUE_EXPR, VAL1_EXPR], C),
             E([FALSE_VALUE_EXPR, VAL2_EXPR], C)])
        # Don't care about result, just don't crash
        self.assertTrue(True)

    def test_cond_with_else(self):
        # Even if 'else' is set to False, check that else in a cond
        # evals to true
        self.set_namespace({'else': False})
        self.assert_special_form_returns(
            self.env._cond,
            [E([FALSE_VALUE_EXPR, VAL1_EXPR], C), E([ELSE_EXPR, VAL2_EXPR], C)],
            2)

    def test_cond_with_list_of_expressions(self):
        self.assert_special_form_returns(
            self.env._cond,
            [E([TRUE_VALUE_EXPR, VAL1_EXPR, VAL2_EXPR], C)],
            2)

    def test_ill_formed_cond_throws_error(self):
        # Only predicate, no consequent expression.  Make sure some
        # kind of exception is raised.
        self.assertRaises(Exception,
                          self.call_special_form, self.env._cond, ['1'])

    def test_if_true(self):
        self.assert_special_form_returns(
            self.env._if,
            [TRUE_VALUE_EXPR, VAL1_EXPR, VAL2_EXPR],
            1)

    def test_if_false(self):
        self.assert_special_form_returns(
            self.env._if,
            [FALSE_VALUE_EXPR, VAL1_EXPR, VAL2_EXPR],
            2)

    def test_and_all_true(self):
        self.assert_special_form_returns(
            self.env._and,
            [TRUE_VALUE_EXPR, VAL1_EXPR],
            1)

    def test_and_all_false(self):
        self.assert_special_form_returns(
            self.env._and,
            [FALSE_VALUE_EXPR, FALSE_VALUE_EXPR],
            False)

    def test_and_one_false(self):
        self.assert_special_form_returns(
            self.env._and,
            [VAL1_EXPR, FALSE_VALUE_EXPR],
            False)

    def test_or_all_false(self):
        self.assert_special_form_returns(
            self.env._or,
            [FALSE_VALUE_EXPR, FALSE_VALUE_EXPR],
            False)

    def test_or_all_true(self):
        self.assert_special_form_returns(
            self.env._or,
            [VAL1_EXPR, TRUE_VALUE_EXPR],
            1)

    def test_or_one_true(self):
        self.assert_special_form_returns(
            self.env._or,
            [FALSE_VALUE_EXPR, VAL1_EXPR],
            1)


class test_builtins(TestCase):
    def test_add_three_operands(self):
        result = Builtins.add([1, 2, 3])
        self.assertEqual(6, result)

    def test_subtract_two_operands(self):
        result = Builtins.subtract([3, 2])
        self.assertEqual(1, result)

    def test_subtract_three_operands(self):
        result = Builtins.subtract([3, 2, 1])
        self.assertEqual(0, result)

    def test_subtract_one_operand_negation(self):
        result = Builtins.subtract([1])
        self.assertEqual(-1, result)

    def test_multiply_three_operands(self):
        result = Builtins.multiply([1, 2, 3])
        self.assertEqual(6, result)

    def test_divide_two_operands(self):
        result = Builtins.divide([6, 2])
        self.assertEqual(3, result)

    def test_divide_three_operands(self):
        result = Builtins.divide([12, 3, 2])
        self.assertEqual(2, result)

    def test_not_true(self):
        result = Builtins.not_([False])
        self.assertTrue(result)

    def test_not_false(self):
        result = Builtins.not_([True])
        self.assertFalse(result)

    def test_greater_than(self):
        result = Builtins.greater_than([4, 3])
        self.assertTrue(result)
        result = Builtins.greater_than([4, 4])
        self.assertFalse(result)

    def test_less_than(self):
        result = Builtins.less_than([3, 4])
        self.assertTrue(result)
        result = Builtins.less_than([4, 4])
        self.assertFalse(result)

    def test_equals(self):
        result = Builtins.equals([3, 3])
        self.assertTrue(result)
        result = Builtins.equals([3, 4])
        self.assertFalse(result)

    def test_abs(self):
        result = Builtins.abs([3])
        self.assertEqual(3, result)
        result = Builtins.abs([-3])
        self.assertEqual(3, result)

    def test_reamainder(self):
        result = Builtins.remainder([3, 3])
        self.assertEqual(0, result)
        result = Builtins.remainder([5, 3])
        self.assertEqual(2, result)


class test_procedure(TestCase):
    def setUp(self):
        self.env = Environment()

    def set_namespace(self, namespace):
        self.env.namespace = namespace

    def assert_procedure_results(self, procedure, parameters, args, outp):
        """Assert procedure returns expected results.

        Call scheme procedure defined by procedure, with parameters
        set to args.  Assert return value is equal to outp.
        """

        p = Procedure(procedure, parameters)
        result = p.apply(self.env, args)
        self.assertEqual(result, outp)

    def test_equality_true(self):
        """Test that identical Procedure objects compares to true.

        Procedures are compared for equality in tests that set the
        namespace of the environment, containing procedures."""

        p1 = Procedure(add)
        p2 = Procedure(add)
        p3 = Procedure([['foo', 'a']], parameters=['a'])
        p4 = Procedure([['foo', 'a']], parameters=['a'])
        self.assertTrue(p1 == p2)
        self.assertTrue(p3 == p4)
        self.assertFalse(p1 != p2)
        self.assertFalse(p3 != p4)
        
    def test_equality_false(self):
        """Test that different Procedure objects compares to false.

        Procedures are compared for equality in tests that set the
        namespace of the environment, containing procedures."""

        p1 = Procedure(add)
        p2 = Procedure(sum)
        p3 = Procedure([['foo', 'a']], parameters=['a'])
        p4 = Procedure([['foo', 'a']])
        p5 = Procedure([['bar', 'a']])
        self.assertTrue(p1 != p2)
        self.assertTrue(p3 != p4)
        self.assertTrue(p4 != p5)
        self.assertFalse(p1 == p2)
        self.assertFalse(p3 == p4)
        self.assertFalse(p4 == p5)

    def test_apply_combination(self):
        """Test that a compound procedure is correctly applied."""

        self.set_namespace({PROC_NAME: BuiltinProcedure(add)})
        self.assert_procedure_results(
            [E([PROC_NAME_EXPR, PM1_EXPR, PM2_EXPR], C)],
            [PM1, PM2],
            [1, 2], 3)

    def test_apply_primitive_body(self):
        """Test procedure with body only consisting of a primitive."""

        self.assert_procedure_results([PM1_EXPR], [PM1], [42], 42)

    def test_apply_list_of_expressions(self):
        """Test procedure with more than one expression."""

        self.assert_procedure_results([PM1_EXPR, NUMERIC_VAL_EXPR],
                                      [PM1], [42], NUMERIC_VAL)


class test_builtin_procedure(TestCase):
    def test_builtin_python_function(self):
        """Test primitive procedure, implemented in Python"""

        p = BuiltinProcedure(add)
        result = p.apply(None, [1, 2])
        self.assertEqual(result, 3)


if __name__ == '__main__':
    main()
