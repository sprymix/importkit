from semantix.lang.yaml import validator


class YamlValidationError(Exception):
    pass


class Base(validator.Schema):
    def get_import_context_class(self):
        pass


class Schema(Base):
    def check(self, node):
        node.tag = 'tag:semantix.sprymix.com,2009/semantix/class/derive:semantix.lang.yaml.schema.Base'
        return node
