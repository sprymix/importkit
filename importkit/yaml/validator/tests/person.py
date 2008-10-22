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
        name: Yuri Selivanov
        phone: 416-509-280
        """

    @failUnlessException(validator.SchemaValidationError, 'pattern validation failed')
    def test_validator_pattern(self):
        """
        - name: Yuri Selivanov
          phone: 416-509-280
        """

    @failUnlessException(validator.SchemaValidationError, 'range-max validation failed')
    def test_validator_range_max(self):
        """
        - name: "123456789012345678901"
          phone: 416-509-2801
        """

def suite():
    return unittest.defaultTestLoader.loadTestsFromTestCase(PersonTests)

if __name__ == '__main__':
    unittest.main()
