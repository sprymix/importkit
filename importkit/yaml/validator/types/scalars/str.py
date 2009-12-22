from .base import SchemaTextType
from ...error import SchemaValidationError

class StringType(SchemaTextType):
    def check(self, node):
        if node.tag != 'tag:yaml.org,2002:str':
            raise SchemaValidationError('expected string', node)

        return super().check(node)
