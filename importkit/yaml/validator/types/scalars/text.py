from .base import SchemaTextType
from ...error import SchemaValidationError

class TextType(SchemaTextType):
    def check(self, data, path):
        if not isinstance(data, int) and not isinstance(data, float) and not isinstance(data, str):
            raise SchemaValidationError('expected text (number or str)', path)

        return str(super(TextType, self).check(data, path))
