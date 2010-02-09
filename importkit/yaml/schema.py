##
# Copyright (c) 2008-2010 Sprymix Inc.
# All rights reserved.
#
# See LICENSE for details.
##


from semantix.lang.yaml import validator


class YamlValidationError(Exception):
    pass


class Base(validator.Schema):
    def get_import_context_class(self):
        pass


class Schema(Base):
    def check(self, node):
        if not hasattr(node, 'tags'):
            node.tags = [node.tag]
        else:
            node.tags.add(node.tag)
        node.tag = 'tag:semantix.sprymix.com,2009/semantix/class/derive:semantix.lang.yaml.schema.Base'
        return node
