import unittest
import yaml

from semantix.lib import validator, readers
from .base import *

class ChoiceTests(SchemaTest):
    def setUp(self):
        self.schema = self.get_schema('ymls/choice.yml')

    @failUnlessException(validator.SchemaValidationError, 'Choice block errors')
    def test_validator_root_sequence(self):
        """
        constraints:
            - expr1: |
                Hello World
            - regexp: ^test$
        """

def suite():
    return unittest.defaultTestLoader.loadTestsFromTestCase(ChoiceTests)

if __name__ == '__main__':
    unittest.main()
