##
# Copyright (c) 2012 Sprymix Inc.
# All rights reserved.
#
# See LICENSE for details.
##


from importkit.meta import Object
from importkit.yaml.validator.tests.base import SchemaTest, raises, result


class A(Object):
    def __init__(self, test1, test2):
        self.test1 = test1
        self.test2 = test2

    def __eq__(self, other):
        return isinstance(other, A) and other.test1 == self.test1 and other.test2 == self.test2

    def __sx_setstate__(self, data):
        self.test1 = data['test1']
        self.test2 = data['test2']


class TestInheritance(SchemaTest):
    def setUp(self):
        super().setUp()
        self.schema = self.get_schema('inheritance.Schema')

    @result(expected_result=A(test1=1, test2='str2'))
    def test_validator_inheritance1(self):
        """
        test1: 1
        test2: str2
        """

    @raises(Exception, 'expected integer')
    def test_validator_inheritance2(self):
        """
        test1: wrong
        test2: 2
        """
