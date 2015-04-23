##
# Copyright (c) 2008-2010 Sprymix Inc.
# All rights reserved.
#
# See LICENSE for details.
##


import py
from semantix.lang.yaml import validator
from semantix.lang.yaml.validator.tests.base import SchemaTest, raises, result


class TestChoice(SchemaTest):
    @staticmethod
    def setup_class(cls):
        cls.schema = cls.get_schema('ymls/choice.yml')

    @py.test.mark.skipif(True)
    @raises(validator.SchemaValidationError, 'Choice block errors')
    def test_validator_choice1(self):
        """
        constraints:
            - expr1: |
                Hello World
            - regexp: ^test$
        """

    @py.test.mark.skipif(True)
    @raises(validator.SchemaValidationError, 'expected string')
    def test_validator_choice2(self):
        """
        constraints:
            - expr: |
                Hello World
            - regexp: ^test$
            - expr: 123
        """

    @result({'constraints': [{'expr': 'Hello World\n'}, {'regexp': '^test$'}]})
    def test_validator_choice_result1(self):
        """
        constraints:
            - expr: |
                Hello World
            - regexp: ^test$
        """

    @result({'constraints': [{'expr': '126'}, {'expr': '124'}, {'expr': '124'}]})
    def test_validator_choice_result2(self):
        """
        constraints:
            - expr: '126'
            - expr: '124'
            - expr: '124'
        """

    @result({'constraints': [{'expr': '126'}, {'constraints': [{'min-length': 1}]}]})
    def test_validator_choice_result3(self):
        """
        constraints:
            - expr: '126'
            - constraints:
                - min-length: 1
        """
