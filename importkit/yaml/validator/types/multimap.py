##
# Copyright (c) 2012-2013 Sprymix Inc.
# All rights reserved.
#
# See LICENSE for details.
##


import yaml
import yaml.representer

from .composite import CompositeType
from ..error import SchemaValidationError


class multimap(list):
    pass


class MultiMappingType(CompositeType):
    __slots__ = ['mapping_type']

    def __init__(self, schema):
        super().__init__(schema)
        self.mapping_type = None

    def default_node_type(self):
        return yaml.nodes.SequenceNode

    def load(self, dct):
        super().load(dct)
        self._init_constrainrs(('max-length', 'min-length'), dct)
        self.mapping_type = self.schema._build(dct['mapping']['='])

    def check(self, node):
        super().check(node)

        if not isinstance(node, yaml.nodes.MappingNode):
            raise SchemaValidationError('series of mappings expected', node)

        self.check_constraints(node)

        self.mapping_type.begin_checks()
        new_list = []

        for key, value in node.value:
            new_list.append((key, self.mapping_type.check(value)))

        node.value = new_list
        self.mapping_type.end_checks()

        if (node.tag.startswith('tag:importkit.magic.io,2009/importkit/class/derive:')
                or node.tag.startswith('tag:importkit.magic.io,2009/importkit/object/create:')):
            node.tags.append('tag:importkit.magic.io,2009/importkit/multimap')
        else:
            self.push_tag(node, 'tag:importkit.magic.io,2009/importkit/multimap')

        return node


class MultiMappingTypeRepresenter(yaml.representer.Representer):
    def represent_multimap(self, data):
        return self.represent_mapping('tag:importkit.magic.io,2009/importkit/multimap', data)


yaml.representer.Representer.add_representer(multimap,
        MultiMappingTypeRepresenter.represent_multimap)
