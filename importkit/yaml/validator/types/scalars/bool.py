from ..base import SchemaType
from ...error import SchemaValidationError

class BoolType(SchemaType):
    def check(self, data, path):
        if not isinstance(data, bool):
            raise SchemaValidationError('expected bool', path)

        return super(BoolType, self).check(data, path)
