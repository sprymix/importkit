import unittest
import yaml

from semantix.lib import validator, readers
from .base import *

class Tests(unittest.TestCase):
    def setUp(self):
        self.schema = validator.Schema(readers.read('ymls/person.yml'))

    def load(self, str):
        return yaml.load(str)

    @failUnlessException(validator.SchemaValidationError, 'list expected')
    def test_root_sequence(self):
        """
        name: Yuri Selivanov
        phone: 416-509-280
        """

    @failUnlessException(validator.SchemaValidationError, 'pattern validation failed')
    def test_pattern(self):
        """
        - name: Yuri Selivanov
          phone: 416-509-280
        """

    @failUnlessException(validator.SchemaValidationError, 'range-max validation failed')
    def test_range_max(self):
        """
        - name: "123456789012345678901"
          phone: 416-509-2801
        """


if __name__ == '__main__':
    unittest.main()
