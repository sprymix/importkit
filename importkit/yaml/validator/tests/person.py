import unittest
import yaml

from semantix.lib import validator, readers
from .base import *

class PersonTests(SchemaTest):
    def setUp(self):
        self.schema = self.get_schema('ymls/person.yml')

    @failUnlessException(validator.SchemaValidationError, 'list expected')
    def test_validator_root_sequence(self):
        """
        name: Yuri
        phone: 416-509-280
        """

    @failUnlessException(validator.SchemaValidationError, 'pattern validation failed')
    def test_validator_pattern(self):
        """
        - name: Yuri
          phone: 416-509-280
        """

    @failUnlessException(validator.SchemaValidationError, 'range-max validation failed')
    def test_validator_range_max(self):
        """
        - name: "123456789012345678901"
          phone: 416-509-2801
        """

    @failUnlessResult([{'phone': '416-509-2801', 'name': 'John', 'sex': 'male'}])
    def test_validator_default1(self):
        """
        - name: "John"
          phone: 416-509-2801
        """

    @failUnlessException(validator.SchemaValidationError, 'enum validation failed')
    def test_validator_enum1(self):
        """
        - name: "John"
          phone: 416-509-2801
          sex: unknown
        """

    @failUnlessException(validator.SchemaValidationError, 'unique key "name", value "Anya" is already used')
    def test_validator_unique(self):
        """
        - name: "Anya"
          phone: 416-509-2801
          sex: female
        - name: "Anya"
          phone: 416-509-2801
          sex: female
        """

    @failUnlessResult([{'phone': '416-509-2801', 'name': 'Anya', 'sex': 'female'},
                       {'phone': '416-509-2101', 'name': 'John Doe', 'sex': 'male'}])
    def test_validator_person_seq1(self):
        """
        - name: "Anya"
          phone: 416-509-2801
          sex: female
        - name: "John Doe"
          phone: 416-509-2101
        """


def suite():
    return unittest.defaultTestLoader.loadTestsFromTestCase(PersonTests)

if __name__ == '__main__':
    unittest.main()
