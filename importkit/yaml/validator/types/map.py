import copy
import yaml

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

        self._init_constrainrs(('max-length', 'min-length'), dct)

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

    def check(self, node):
        super().check(node)

        """ XXX:
        did = id(data)
        if did in self.checked:
            return data
        self.checked[did] = True
        """

        if node.tag == 'tag:yaml.org,2002:null':
            node = yaml.nodes.MappingNode(tag='tag:yaml.org,2002:map', value=[])
        elif not isinstance(node, yaml.nodes.MappingNode):
            raise SchemaValidationError('mapping expected', node)

        if 'min-length' in self.constraints:
            if len(node.value) < self.constraints['min-length']:
                raise SchemaValidationError('the number of elements in mapping must not be less than %d'
                                            % self.constraints['min-length'], node)

        if 'max-length' in self.constraints:
            if len(node.value) > self.constraints['max-length']:
                raise SchemaValidationError('the number of elements in mapping must not exceed %d'
                                            % self.constraints['max-length'], node)

        any = '=' in self.keys

        for i, (key, value) in enumerate(node.value):
            # TODO: support non-scalar keys
            conf_key = key.value
            if key.value in self.keys:
                conf = self.keys[key.value]
            elif any:
                conf_key = '='
                conf = self.keys['=']
            else:
                raise SchemaValidationError('unexpected key "%s"' % key.value, node)

            if conf['required'] and value.value is None:
                raise SchemaValidationError('None value for required key "%s"' % key, node)

            conf['type'].begin_checks()
            value = conf['type'].check(value)
            conf['type'].end_checks()

            if conf['unique']:
                if value.value in self.unique[conf_key]:
                    raise SchemaValidationError('unique key "%s", value "%s" is already used in %s' %
                                                (key.value, value.value, self.unique[conf_key][value.value]))

                self.unique[conf_key][value.value] = value

            node.value[i] = (key, value)

        value = {key.value: (key, value) for key, value in node.value}

        for key, conf in self.keys.items():
            if key == '=':
                continue

            if key not in value:
                if 'default' in conf:
                    node.value.append((yaml.nodes.ScalarNode(value=key, tag='tag:yaml.org,2002:str'),
                                       self.coerse_value(conf['type'], conf['default'], node)))

                else:
                    if conf['required']:
                        raise SchemaValidationError('key "%s" is required' % key, node)
                    else:
                        k = yaml.nodes.ScalarNode(value=key, tag='tag:yaml.org,2002:str')
                        v = yaml.nodes.ScalarNode(value=None, tag='tag:yaml.org,2002:null')
                        node.value.append((k, v))

        return node
