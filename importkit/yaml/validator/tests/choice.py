import unittest
import yaml

from semantix import validator, readers
from .base import *

class ChoiceTests(SchemaTest):
    def setUp(self):
        self.schema = self.get_schema('ymls/choice.yml')

    @failUnlessException(validator.SchemaValidationError, 'Choice block errors')
    def test_validator_choice1(self):
        """
        constraints:
            - expr1: |
                Hello World
            - regexp: ^test$
        """

    @failUnlessException(validator.SchemaValidationError, 'expected string')
    def test_validator_choice2(self):
        """
        constraints:
            - expr: |
                Hello World
            - regexp: ^test$
            - expr: 123
        """

    @failUnlessResult({'constraints': [{'expr': 'Hello World\n'}, {'regexp': '^test$'}]})
    def test_validator_choice_result1(self):
        """
        constraints:
            - expr: |
                Hello World
            - regexp: ^test$
        """

    @failUnlessResult({'constraints': [{'expr': '126'}, {'expr': '124'}, {'expr': '124'}]})
    def test_validator_choice_result2(self):
        """
        constraints:
            - expr: '126'
            - expr: '124'
            - expr: '124'
        """

    @failUnlessResult({'constraints': [{'expr': '126'}, {'constraints': [{'min-length': 1}]}]})
    def test_validator_choice_result3(self):
        """
        constraints:
            - expr: '126'
            - constraints:
                - min-length: 1
        """

def suite():
    return unittest.defaultTestLoader.loadTestsFromTestCase(ChoiceTests)

if __name__ == '__main__':
    unittest.main()
