import unittest
import yaml

from semantix import validator, readers
from .base import *

class TypesTests(SchemaTest):
    def setUp(self):
        self.schema = self.get_schema('ymls/types.yml')

    @failUnlessException(validator.SchemaValidationError, 'expected integer')
    def test_validator_types_int_fail1(self):
        """
        int: '12'
        """

    @failUnlessException(validator.SchemaValidationError, 'expected integer')
    def test_validator_types_int_fail2(self):
        """
        int: 123.2
        """

    @failUnlessResult(key='int', value=31415)
    def test_validator_types_int_result(self):
        """
        int: 31415
        """

    @failUnlessException(validator.SchemaValidationError, 'expected number (int or float)')
    def test_validator_types_number_fail1(self):
        """
        number: [123, 1]
        """

    @failUnlessResult(key='number', value=31415)
    def test_validator_types_number_int_result(self):
        """
        number: 31415
        """

    @failUnlessResult(key='number', value=31415.2)
    def test_validator_types_number_float_result(self):
        """
        number: 31415.2
        """

    @failUnlessException(validator.SchemaValidationError, 'expected text (number or str)')
    def test_validator_types_text_fail1(self):
        """
        text: [123, 1]
        """

    @failUnlessResult(key='text', value='31415')
    def test_validator_types_text_int_result(self):
        """
        text: 31415
        """

    @failUnlessResult(key='text', value='31415.123')
    def test_validator_types_text_float_result(self):
        """
        text: 31415.123
        """

    @failUnlessResult(key='bool', value=True)
    def test_validator_types_bool_yes_result(self):
        """
        bool: yes
        """

    @failUnlessResult(key='bool', value=True)
    def test_validator_types_bool_True_result(self):
        """
        bool: True
        """

    @failUnlessResult(key='bool', value=True)
    def test_validator_types_bool_true_result(self):
        """
        bool: true
        """

    @failUnlessResult(key='bool', value=False)
    def test_validator_types_bool_yes_result(self):
        """
        bool: no
        """

    @failUnlessResult(key='bool', value=False)
    def test_validator_types_bool_True_result(self):
        """
        bool: false
        """

    @failUnlessException(validator.SchemaValidationError, 'expected bool')
    def test_validator_types_bool_fail1(self):
        """
        bool: 1
        """

    @failUnlessException(validator.SchemaValidationError, 'expected bool')
    def test_validator_types_bool_fail2(self):
        """
        bool: 'yes'
        """


def suite():
    return unittest.defaultTestLoader.loadTestsFromTestCase(TypesTests)

if __name__ == '__main__':
    unittest.main()
