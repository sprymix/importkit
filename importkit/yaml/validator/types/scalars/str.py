from .base import SchemaTextType
from ...error import SchemaValidationError

class StringType(SchemaTextType):
    def check(self, data, path):
        if not isinstance(data, str):
            raise SchemaValidationError('expected string', path)

        return super(StringType, self).check(data, path)
