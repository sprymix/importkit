from .base import SchemaScalarType
from ...error import SchemaValidationError

class NumberType(SchemaScalarType):
    def check(self, data, path):
        if not isinstance(data, int) and not isinstance(data, float):
            raise SchemaValidationError('expected number (int or float)', path)

        return super(NumberType, self).check(data, path)
