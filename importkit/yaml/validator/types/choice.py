import copy

from .base import SchemaType
from ..error import SchemaValidationError

class ChoiceType(SchemaType):
    __slots__ = ['choice']

    def __init__(self, schema):
        super(ChoiceType, self).__init__(schema)
        self.choice = None

    def load(self, dct):
        super(ChoiceType, self).load(dct)

        self.choice = []
        for choice in dct['choice']:
            self.choice.append(self.schema._build(choice))


    def check(self, data, path):
        super(ChoiceType, self).check(data, path)

        errors = []
        tmp = None

        for choice in self.choice:
            try:
                tmp = copy.deepcopy(data)
                tmp = choice.check(tmp, path)
            except SchemaValidationError, error:
                errors.append(str(error))
            else:
                break
        else:
            raise SchemaValidationError('Choice block errors:\n' + '\n'.join(errors), path)

        data = tmp
        return data
