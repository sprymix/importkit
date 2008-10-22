import unittest
from semantix.lib.validator.tests.choice import suite as choice_suite
from semantix.lib.validator.tests.person import suite as person_suite

def suite():
    suite = unittest.TestSuite();
    suite.addTest(choice_suite())
    suite.addTest(person_suite())
    return suite
