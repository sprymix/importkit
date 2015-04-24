##
# Copyright (c) 2008-2012 Sprymix Inc.
# All rights reserved.
#
# See LICENSE for details.
##


from . import types as v_types
from . import validator


class YamlValidationError(Exception):
    pass


class Base(validator.Schema):
    def get_import_context_class(self):
        pass

    @classmethod
    def get_module_class(cls):
        raise NotImplementedError

    @classmethod
    def get_implicit_imports(cls):
        return ()

    @classmethod
    def normalize_code(cls, module_data, imports):
        pass

    @classmethod
    def get_schema_magic(cls):
        return 0


class ModuleSchemaBase(Base):
    pass


class NamespaceModuleSchemaBase(ModuleSchemaBase):
    def check(self, node):
        node = super().check(node)
        node.tag = 'tag:importkit.magic.io,2009/importkit/schema/namespace'
        return node


class Schema(Base):
    _schema_base_cls = Base

    def check(self, node):
        if not hasattr(node, 'tags'):
            node.tags = [node.tag]
        else:
            node.tags.append(node.tag)
        tag = 'tag:importkit.magic.io,2009/importkit/class/derive:{}.{}'
        node.tag = tag.format(self._schema_base_cls.__module__, self._schema_base_cls.__name__)
        return node


class ModuleSchema(Schema):
    _schema_base_cls = ModuleSchemaBase


class NamespaceModuleSchema(ModuleSchema):
    _schema_base_cls = NamespaceModuleSchemaBase


class CachingSchema:
    @classmethod
    def cacheable(cls):
        return True


class LazyImportsSchema:
    lazy_imports = True
