import copy

from .composite import CompositeType
from ..error import SchemaValidationError

class MappingType(CompositeType):
    __slots__ = ['keys', 'unique_base', 'unique']

    def __init__(self, schema):
        super(MappingType, self).__init__(schema)
        self.keys = {}

        self.unique_base = {}
        self.unique = None

    def load(self, dct):
        super(MappingType, self).load(dct)

        for key, value in dct['mapping'].items():
            self.keys[key] = {}

            self.keys[key]['required'] = 'required' in value and value['required']
            self.keys[key]['unique'] = 'unique' in value and value['unique']

            if self.keys[key]['unique']:
                self.unique_base[key] = {}

            if 'default' in value:
                self.keys[key]['default'] = value['default']

            self.keys[key]['type'] = self.schema._build(value)

    def begin_checks(self):
        super(MappingType, self).begin_checks()
        self.unique = copy.deepcopy(self.unique_base)

    def end_checks(self):
        super(MappingType, self).end_checks()
        self.unique = None

    def check(self, data, path):
        super(MappingType, self).check(data, path)

        did = id(data)
        if did in self.checked:
            return data
        self.checked[did] = True

        if not isinstance(data, dict):
            raise SchemaValidationError('mapping expected', path)

        any = '=' in self.keys

        for key, value in data.items():
            conf_key = key
            if key in self.keys:
                conf = self.keys[key]
            elif any:
                conf_key = '='
                conf = self.keys['=']
            else:
                raise SchemaValidationError('unexpected key "%s"' % key, path)

            if conf['required'] and value is None:
                raise SchemaValidationError('None value for required key "%s"' % key, path)

            if value is not None:
                conf['type'].begin_checks()
                data[key] = conf['type'].check(value, path + '/' + key)
                conf['type'].end_checks()

            if conf['unique']:
                if value in self.unique[conf_key]:
                    raise SchemaValidationError('unique key "%s", value "%s" is already used in %s' %
                                                (key, value, self.unique[conf_key][value]))

                self.unique[conf_key][value] = path

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
