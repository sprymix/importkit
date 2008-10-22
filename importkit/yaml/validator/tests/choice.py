import unittest
import yaml

from semantix.lib import validator, readers
from .base import *

class Tests(unittest.TestCase):
    def setUp(self):
        self.schema = validator.Schema(readers.read('ymls/choice.yml'))

    def load(self, str):
        return yaml.load(str)

    @failUnlessException(validator.SchemaValidationError, 'Choice block errors')
    def test_root_sequence(self):
        """
        constraints:
            - exp1r: Hello World
            - regexp: ^test$
        """

if __name__ == '__main__':
    unittest.main()
