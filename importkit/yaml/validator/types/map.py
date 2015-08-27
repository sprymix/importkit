##
# Copyright (c) 2008-2010, 2015 Sprymix Inc.
# All rights reserved.
#
# See LICENSE for details.
##


import collections
import copy
import re
import yaml

from .composite import CompositeType
from ..error import SchemaValidationError


class AnyValue:
    def match(self, value):
        return True

    def __repr__(self):
        return '<any value>'

    @property
    def pattern(self):
        return '='


class RegExp:
    def __init__(self, pattern):
        self._re = re.compile(pattern)

    def match(self, value):
        if isinstance(value, str):
            return self._re.match(value)
        else:
            return False

    def __repr__(self):
        return repr(self._re)

    @property
    def pattern(self):
        return self._re.pattern


class MappingType(CompositeType):
    __slots__ = ['keys', 'key_res', 'unique_base', 'unique', 'ordered']

    def __init__(self, schema):
        super().__init__(schema)
        self.keys = collections.OrderedDict()
        self.key_res = []

        self.unique_base = {}
        self.unique = None

    def default_node_type(self):
        return yaml.nodes.MappingNode

    def load_keys(self, keys):
        for key, value in keys.items():
            if key == '=':
                key = AnyValue()
                self.key_res.append(key)
            elif key.startswith('/') and key.endswith('/'):
                key = RegExp(key[1:-1])
                self.key_res.append(key)

            self.keys[key] = {}

            if isinstance(value, dict):
                self.keys[key]['required'] = bool(value.get('required'))
                self.keys[key]['unique'] = bool(value.get('unique'))

                if self.keys[key]['unique']:
                    self.unique_base[key] = {}

                if 'default' in value:
                    self.keys[key]['default'] = value['default']
            else:
                self.keys[key]['required'] = False
                self.keys[key]['unique'] = False

            self.keys[key]['type'] = self.schema._build(value)

    def load(self, dct):
        super(MappingType, self).load(dct)

        self._init_constrainrs(('max-length', 'min-length'), dct)
        self.load_keys(dct['mapping'])
        self.ordered = dct.get('ordered', False)

    def begin_checks(self):
        super(MappingType, self).begin_checks()
        self.unique = copy.deepcopy(self.unique_base)

    def end_checks(self):
        super(MappingType, self).end_checks()
        self.unique = None

    def _match_key(self, key_value):
        conf = None

        try:
            conf = self.keys[key_value]
        except KeyError:
            for key_re in self.key_res:
                if key_re.match(key_value):
                    conf = self.keys[key_re]
                    key_value = key_re.pattern

        return key_value, conf

    def check(self, node):
        node = super().check(node)

        if node.tag == 'tag:yaml.org,2002:null':
            node = yaml.nodes.MappingNode(tag='tag:yaml.org,2002:map',
                                          value=[],
                                          start_mark=node.start_mark,
                                          end_mark=node.end_mark)
        elif not isinstance(node, yaml.nodes.MappingNode):
            raise SchemaValidationError('mapping expected', node)

        self.check_constraints(node)

        keys = set()

        for i, (key, value) in enumerate(node.value):
            subschema = self.get_subschema(key)

            if isinstance(key.value, list):
                key.tag = 'tag:yaml.org,2002:python/tuple'
                key.value = tuple(key.value)
                key_value = tuple(v.value for v in key.value)
            else:
                key_value = key.value

            if key_value in keys:
                err = 'duplicate mapping key {!r}'.format(key_value)
                raise SchemaValidationError(err, node)

            conf_key, conf = self._match_key(key_value)

            if conf is None:
                err = 'unexpected key {!r}'.format(key_value)
                raise SchemaValidationError(err, node)

            if conf['required'] and value.value is None:
                err = 'None value for required key {!r}'.format(key_value)
                raise SchemaValidationError(err, node)

            if subschema is not None:
                value = subschema.check(value)
            else:
                conf['type'].begin_checks()
                value = conf['type'].check(value)
                conf['type'].end_checks()

            if conf['unique']:
                if value.value in self.unique[conf_key]:
                    err = 'unique key {!r}, value {!r} is already used in {!r}'
                    err = err.format(key_value, value.value,
                                     self.unique[conf_key][value.value])
                    raise SchemaValidationError(err, node)

                self.unique[conf_key][value.value] = value

            node.value[i] = (key, value)
            keys.add(key.value)

        value = {key.value: (key, value) for key, value in node.value}

        for key, conf in self.keys.items():
            if hasattr(key, 'match'):
                # Skip RE keys
                continue

            if key not in value:
                if 'default' in conf:
                    key = yaml.nodes.ScalarNode(
                                value=key, tag='tag:yaml.org,2002:str')
                    default = self.coerse_value(
                                conf['type'], conf['default'], node)
                    node.value.append((key, default))

                else:
                    if conf['required']:
                        err = 'key {!r} is required'.format(key)
                        raise SchemaValidationError(err, node)
                    else:
                        k = yaml.nodes.ScalarNode(
                                value=key, tag='tag:yaml.org,2002:str')
                        v = yaml.nodes.ScalarNode(
                                value=None, tag='tag:yaml.org,2002:null')
                        node.value.append((k, v))

        if self.ordered:
            self.push_tag(
                node, 'tag:importkit.magic.io,2009/importkit/orderedmap')

        return node
