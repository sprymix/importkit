import unittest
import yaml

from semantix.lib import validator, readers
from .base import *

class Unique1Tests(SchemaTest):
    def setUp(self):
        self.schema = self.get_schema('ymls/unique1.yml')

    @failUnlessException(Exception, 'unique value "test" is already used')
    def test_validator_unique_map_key(self):
        """
        test1:
            - test
            - test
        """

    @failUnlessException(Exception, 'unique value "2" is already used')
    def test_validator_unique_map_key2(self):
        """
        test1:
            - test
            - test2
        test2:
            - 2
            - 2
        """

    @failUnlessException(Exception, 'enum validation failed')
    def test_validator_unique_map_key_enum_error(self):
        """
        test1:
            - test
            - test2
        test2:
            - 0
            - 0
        """


def suite():
    return unittest.defaultTestLoader.loadTestsFromTestCase(Unique1Tests)

if __name__ == '__main__':
    unittest.main()
