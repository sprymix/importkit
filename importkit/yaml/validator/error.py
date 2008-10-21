class SchemaValidationError(Exception):
    def __init__(self, value, path=None):
        if path is not None:
            value = path + ': ' + value

        super(SchemaValidationError, self).__init__(value)

class SchemaError(Exception): pass
