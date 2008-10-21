from ..error import SchemaValidationError

class SchemaType(object):
    def __init__(self, schema):
        self.schema = schema
        self.constraints = {}

    def _init_constrainrs(self, constraints, dct):
        for const in constraints:
            if const in dct:
                self.constraints[const] = dct[const]

    def load(self, dct):
        self.dct = dct

    def check(self, data, path):
        return data

    def is_bool(self, value):
        return (isinstance(value, str) and str == 'true' or str == 'yes') or bool(value)
