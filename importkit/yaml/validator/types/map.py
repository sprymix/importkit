from .base import SchemaType
from ..error import SchemaValidationError

class MappingType(SchemaType):
    def __init__(self, schema):
        super(MappingType, self).__init__(schema)
        self.keys = {}

    def load(self, dct):
        super(MappingType, self).load(dct)

        for key, value in dct['mapping'].items():
            self.keys[key] = {}

            self.keys[key]['required'] = 'required' in value and value['required']
            if 'default' in value:
                self.keys[key]['default'] = value['default']

            self.keys[key]['type'] = self.schema._build(value)


    def check(self, data, path):
        super(MappingType, self).check(data, path)

        if not isinstance(data, dict):
            raise SchemaValidationError('mapping expected', path)

        any = '=' in self.keys

        for key, value in data.items():
            if key in self.keys:
                conf = self.keys[key]
            elif any:
                conf = self.keys['=']
            else:
                raise SchemaValidationError('unexpected key "%s"' % key, path)

            if conf['required'] and value is None:
                raise SchemaValidationError('None value for required key "%s"' % key, path)

            if value is not None:
                data[key] = conf['type'].check(value, path + '/' + key)

        for key, conf in self.keys.items():
            if key == '=':
                continue

            if key not in data:
                if 'default' in conf:
                    data[key] = conf['default']

            if key not in data:
                if conf['required']:
                    raise SchemaValidationError('key "%s" is required' % key, path)
                else:
                    data[key] = None

        return data
