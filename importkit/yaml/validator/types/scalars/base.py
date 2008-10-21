import re

from ..base import SchemaType
from ...error import SchemaValidationError

class SchemaScalarType(SchemaType):
    def load(self, dct):
        super(SchemaScalarType, self).load(dct)
        self._init_constrainrs(('enum', 'range'), dct)

    @staticmethod
    def check_range(range, data, repr=None, path=''):
        if repr is None:
            repr = data

        if 'min' in range:
            if data < range['min']:
                raise SchemaValidationError('range-min validation failed, value: "%s" < %s' %
                                            (repr, range['min']), path)

        if 'min-ex' in range:
            if data <= range['min-ex']:
                raise SchemaValidationError('range-min-ex validation failed, value: "%s" <= %s' %
                                            (repr, range['min-ex']), path)

        if 'max' in range:
            if data > range['max']:
                raise SchemaValidationError('range-max validation failed, value: "%s" > %s' %
                                            (repr, range['max']), path)

        if 'max-ex' in range:
            if data > range['max-ex']:
                raise SchemaValidationError('range-max validation failed, value: "%s" >= %s' %
                                            (repr, range['max-ex']), path)

    def check(self, data, path):
        super(SchemaScalarType, self).check(data, path)

        if 'enum' in self.constraints:
            if data not in self.constraints['enum']:
                raise SchemaValidationError('enum validation failed, value: "%s" is not in %s' %
                                            (data, self.constraints['enum']), path)

        if 'range' in self.constraints:
            SchemaScalarType.check_range(self.constraints['range'], data, data, path)

        return data


class SchemaTextType(SchemaScalarType):
    def load(self, dct):
        super(SchemaTextType, self).load(dct)
        self._init_constrainrs(('pattern', 'length'), dct)

    def check(self, data, path):
        super(SchemaTextType, self).check(data, path)

        if 'pattern' in self.constraints:
            if re.match(self.constraints['pattern'], str(data)) is None:
                raise SchemaValidationError('pattern validation failed, value: "%s"' % data, path)

        if 'length' in self.constraints:
            SchemaScalarType.check_range(self.constraints['length'], len(str(data)), 'len("%s")' % data, path)

        return data
