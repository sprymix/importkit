from .base import SchemaScalarType
from ...error import SchemaValidationError

class NumberType(SchemaScalarType):
    def check(self, node):
        if node.tag not in ('tag:yaml.org,2002:int', 'tag:yaml.org,2002:float'):
            raise SchemaValidationError('expected number (int or float)', node)

        return super().check(node)
