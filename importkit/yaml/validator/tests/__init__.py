import unittest
from semantix.lib.validator.tests.choice import suite as choice_suite
from semantix.lib.validator.tests.person import suite as person_suite
from semantix.lib.validator.tests.unique1 import suite as unique1_suite
from semantix.lib.validator.tests.types import suite as types_suite

def suite():
    suite = unittest.TestSuite();
    suite.addTest(choice_suite())
    suite.addTest(person_suite())
    suite.addTest(unique1_suite())
    suite.addTest(types_suite())
    return suite
