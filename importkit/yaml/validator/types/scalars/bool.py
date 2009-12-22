from ..base import SchemaType
from ...error import SchemaValidationError

class BoolType(SchemaType):
    def check(self, node):
        if node.tag != 'tag:yaml.org,2002:bool':
            raise SchemaValidationError('expected bool', node)

        return super().check(node)
