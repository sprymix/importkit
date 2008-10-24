import copy

from .composite import CompositeType
from ..error import SchemaValidationError

class ChoiceType(CompositeType):
    __slots__ = ['choice']

    def __init__(self, schema):
        super(ChoiceType, self).__init__(schema)
        self.choice = None
        self.checked = {}

    def load(self, dct):
        super(ChoiceType, self).load(dct)

        self.choice = []
        for choice in dct['choice']:
            self.choice.append(self.schema._build(choice))


    def check(self, data, path):
        super(ChoiceType, self).check(data, path)

        did = id(data)
        if did in self.checked:
            return data
        self.checked[did] = True

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
