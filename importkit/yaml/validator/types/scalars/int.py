from .base import SchemaScalarType
from ...error import SchemaValidationError

class IntType(SchemaScalarType):
    def check(self, data, path):
        if not isinstance(data, int):
            raise SchemaValidationError('expected integer', path)

        return super(IntType, self).check(data, path)
