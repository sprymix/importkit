from semantix import validator


class YamlValidationError(Exception):
    pass


class Schema(object):
    def check(self, node):
        node.tag = 'tag:semantix.sprymix.com,2009/semantix/class/derive:semantix.readers.yaml.schema.Base'
        return node


class Base(validator.Schema):
    pass
