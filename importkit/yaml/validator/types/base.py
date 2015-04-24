##
# Copyright (c) 2008-2010 Sprymix Inc.
# All rights reserved.
#
# See LICENSE for details.
##


import yaml


class SchemaType(object):
    __slots__ = ['schema', 'schema_tags', 'constraints', 'dct', 'resolver',
                 'checked_items']

    def __init__(self, schema):
        self.schema = schema
        self.schema_tags = schema.get_tags()
        self.constraints = {}
        self.resolver = yaml.resolver.Resolver()

    def _init_constrainrs(self, constraints, dct):
        for const in constraints:
            if const in dct:
                self.constraints[const] = dct[const]

    def get_subschema(self, value):
        from ..schema import Schema

        if value.tag and self.schema.namespace:
            subschema = self.schema.namespace.get(value.tag[1:])
            if (subschema is not None and isinstance(subschema, type)
                                      and issubclass(subschema, Schema)):
                value.tag = 'tag:yaml.org,2002:str'
                return subschema(namespace=self.schema.namespace)

    def load(self, dct):
        self.dct = dct

    def begin_checks(self):
        pass

    def end_checks(self):
        pass

    def check(self, node):
        if (self, node) in self.schema.checked_nodes:
            return node

        node_tag = node.tag
        tagdata = self.schema_tags.get(node_tag)

        if tagdata is not None:
            if tagdata[0]:
                node.tag = tagdata[0][0]
                for tag in tagdata[0][1:]:
                    self.push_tag(node, tag)
            self.push_tag(node, node_tag)

        if 'object' in self.dct:
            tag = 'tag:importkit.magic.io,2009/importkit/object/create:' + self.dct['object']
            self.push_tag(node, tag)
        elif 'class' in self.dct:
            tag = 'tag:importkit.magic.io,2009/importkit/class/derive:' + self.dct['class']
            self.push_tag(node, tag)

        self.schema.checked_nodes.add((self, node))
        return node

    def is_bool(self, value):
        return (isinstance(value, str) and str == 'true' or str == 'yes') or bool(value)

    def coerse_value(self, type, value, node):
        if value is None:
            value = yaml.nodes.ScalarNode(value=None, tag='tag:yaml.org,2002:null')
        else:
            node_type = type.default_node_type()
            tag = self.resolver.resolve(node_type, repr(value), (True, False))

            if issubclass(node_type, yaml.nodes.ScalarNode):
                value = str(value)
            value = node_type(value=value, tag=tag, start_mark=node.start_mark,
                              end_mark=node.end_mark)
            value = type.check(value)

        return value

    def default_node_type(self):
        return yaml.nodes.ScalarNode

    def check_tag(self, node, *tags, allow_null=True):
        if allow_null:
            tags = ('tag:yaml.org,2002:null',) + tags

        for tag in tags:
            if node.tag == tag or (hasattr(node, 'tags') and tag in node.tags):
                break
        else:
            return False
        return True

    def push_tag(self, node, tag):
        if not hasattr(node, 'tags'):
            node.tags = [node.tag]
        else:
            node.tags.append(node.tag)

        node.tag = tag
        return tag
