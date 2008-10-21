from .base import SchemaScalarType
from ...error import SchemaValidationError

class FloatType(SchemaScalarType):
    def check(self, data, path):
        if not isinstance(data, float):
            raise SchemaValidationError('expected float', path)

        return super(FloatType, self).check(data, path)
