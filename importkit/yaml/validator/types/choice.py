##
# Copyright (c) 2008-2010 Sprymix Inc.
# All rights reserved.
#
# See LICENSE for details.
##


import copy

from .composite import CompositeType
from ..error import SchemaValidationError

class ChoiceType(CompositeType):
    __slots__ = 'choice',

    def __init__(self, schema):
        super().__init__(schema)
        self.choice = None

    def load(self, dct):
        super().load(dct)

        self.choice = []
        for choice in dct['choice']:
            self.choice.append(self.schema._build(choice))

    def check(self, node):
        super().check(node)

        errors = []

        tmp = None

        for choice in self.choice:
            tmp = copy.deepcopy(node)

            try:
                tmp = choice.check(tmp)
            except SchemaValidationError as error:
                errors.append(str(error))
            else:
                break
        else:
            raise SchemaValidationError('Choice block errors:\n' + '\n'.join(errors), node)

        node.value = tmp.value
        node.tag = tmp.tag
        node.tags = getattr(tmp, 'tags', [])

        return node
