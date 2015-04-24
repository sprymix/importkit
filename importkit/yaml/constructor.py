##
# Copyright (c) 2008-2012 Sprymix Inc.
# All rights reserved.
#
# See LICENSE for details.
##


import ast
import decimal
import yaml
import importlib
import collections
import copy
import types
from string import Template

from importkit import meta as lang_base
from importkit import context as lang_context
from importkit.import_ import module as module_types, utils as module_utils


class ModuleTag(str):
    pass


class Composer(yaml.composer.Composer):
    def compose_document(self):
        start_document = self.get_event()

        node = self.compose_node(None, None)

        schema = getattr(start_document, 'schema', None)

        doc_imports = getattr(start_document, 'imports', None)

        if schema:
            module, obj = schema.rsplit('.', 1)
            module = importlib.import_module(module)
            schema = getattr(module, obj)

            if doc_imports:
                lazy_imports = getattr(schema, 'lazy_imports', False)
                namespace = self._process_imports(node, doc_imports, lazy_imports)
            else:
                namespace = {}

            schema_instance = schema(namespace=namespace)

            node = schema_instance.check(node)
            node.import_context = schema_instance.get_import_context_class()

            if node.import_context and \
                    not isinstance(self.document_context.import_context, node.import_context):
                self.document_context.import_context = \
                            node.import_context.from_parent(self.document_context.import_context,
                                                            self.document_context.import_context)

        node.schema = schema
        node.document_name = getattr(start_document, 'document_name', None)
        node.imports = doc_imports

        if self.document_context is not None:
            self.document_context.document_name = node.document_name

        self.get_event()
        self.anchors = {}
        return node

    def _process_imports(self, node, node_imports, lazy_imports=False):
        namespace = {}
        imports = {}
        Proxy = module_types.AutoloadingLightProxyModule

        for module_name, tail in node_imports.items():
            try:
                pkg = self.document_context.module.__package__
            except AttributeError:
                pkg = self.document_context.module.__name__

            module_name = module_utils.resolve_module_name(module_name, pkg)

            if getattr(node, 'import_context', None):
                parent_context = self.document_context.import_context
                module_name = node.import_context.from_parent(module_name,
                                                              parent=parent_context)

            if tail and isinstance(tail, dict):
                fromlist = tuple(tail)
                fromdict = tail
                alias = None
            else:
                alias = tail
                fromlist = ()
                fromdict = {}

            if lazy_imports:
                mod = None
            else:
                try:
                    mod = __import__(module_name, fromlist=fromlist)
                except ImportError as e:
                    raise yaml.constructor.ConstructorError(None, None, '%r' % e,
                                                            node.start_mark) from e

            if fromdict:
                for name, alias in fromdict.items():
                    if not alias:
                        alias = name

                    if lazy_imports:
                        namespace[alias] = lang_context.LazyImportAttribute(module=module_name,
                                                                            attribute=name)
                    else:
                        try:
                            modattr = getattr(mod, name)
                        except AttributeError:
                            msg = 'cannot import name {!r}'.format(name)
                            raise yaml.constructor.ConstructorError(None, None, msg,
                                                                    node.start_mark) from None
                        else:
                            if isinstance(modattr, types.ModuleType):
                                modattr = Proxy(modattr.__name__, modattr)
                                imports[alias or name] = modattr
                            namespace[alias or name] = modattr
            else:
                if lazy_imports:
                    topmod = module_name.partition('.')[0]
                    namespace[topmod] = lang_context.LazyImportAttribute(module=module_name)
                else:
                    namespace[mod.__name__] = Proxy(mod.__name__, mod)

                    if module_name != mod.__name__:
                        endmod = importlib.import_module(module_name)
                    else:
                        endmod = mod

                    if alias is None:
                        # XXX: should avoid doing this
                        imports[module_name] = module_types.ModuleInfo(endmod)
                    else:
                        namespace[alias] = Proxy(endmod.__name__, endmod)
                        imports[alias] = module_types.ModuleInfo(endmod)

        self.document_context.imports.update(imports)
        self.document_context.namespace.update(namespace)

        return namespace


class ConstructorContext:
    def __init__(self, constructor, yaml_constructors):
        self.constructor = constructor

        self.simple_constructors, self.multi_constructors = \
                self._sort_constructors(yaml_constructors)

    def _sort_constructors(self, constructors):
        simple = {}
        multi = {}

        for tag, constructor in constructors.items():
            if tag.endswith(':'):
                multi[tag] = constructor
            else:
                simple[tag] = constructor

        return simple, multi

    def __enter__(self):
        self.old_constructors = self.constructor.yaml_constructors
        constructors = self.constructor.yaml_constructors.copy()

        self.old_multi_constructors = self.constructor.yaml_multi_constructors
        multi_constructors = self.constructor.yaml_multi_constructors.copy()

        constructors.update(self.simple_constructors)
        multi_constructors.update(self.multi_constructors)

        self.constructor.yaml_constructors = constructors
        self.constructor.yaml_multi_constructors = multi_constructors

    def __exit__(self, exc_type, exc_value, traceback):
        self.constructor.yaml_constructors = self.old_constructors
        self.constructor.yaml_multi_constructors = self.old_multi_constructors


class Constructor(yaml.constructor.Constructor):
    def __init__(self, context=None):
        super().__init__()
        self.document_context = context
        self.obj_data = {}

    def _get_class_from_tag(self, clsname, node, intent='class'):
        if not clsname:
            raise yaml.constructor.ConstructorError("while constructing a Python %s" % intent, node.start_mark,
                                                    "expected non-empty class name appended to the tag", node.start_mark)

        module_name, class_name = clsname.rsplit('.', 1)

        try:
            module = importlib.import_module(module_name)
            result = getattr(module, class_name)
        except (ImportError, AttributeError) as exc:
            raise yaml.constructor.ConstructorError("while constructing a Python %s" % intent, node.start_mark,
                                                    "could not find %r (%s)" % (clsname, exc), node.start_mark)

        return result

    def _get_source_context(self, node, document_context):
        start = lang_context.SourcePoint(node.start_mark.line, node.start_mark.column,
                                               node.start_mark.pointer)
        end = lang_context.SourcePoint(node.end_mark.line, node.end_mark.column,
                                               node.end_mark.pointer)

        context = lang_context.SourceContext(getattr(self, 'module_name', '<unknown>'),
                                             node.start_mark.buffer,
                                             start, end, document_context,
                                             filename=node.start_mark.name)
        return context

    def _is_object_or_class(self, node):
        return node.tag.startswith('tag:importkit.magic.io,2009/importkit/class/derive:') or \
               node.tag.startswith('tag:importkit.magic.io,2009/importkit/object/create:')

    def constructor_context(self, yaml_constructors):
        return ConstructorContext(self, yaml_constructors)

    def construct_document(self, node):
        context = self._get_source_context(node, self.document_context)
        lang_context.SourceContext.register_object(node, context)

        if node.schema:
            schema_tags = {tag: tdata[1] for tag, tdata in node.schema.get_tags().items()}
        else:
            schema_tags = None

        if schema_tags:
            with self.constructor_context(schema_tags):
                return super().construct_document(node)
        else:
            return super().construct_document(node)

    def construct_python_class(self, parent, node):
        cls = self._get_class_from_tag(parent, node, 'class')
        name = getattr(node, 'document_name', cls.__name__ + '_' + str(id(node)))

        # Call correct class constructor with __prepare__ method
        #

        try:
            import_context = self.document_context.import_context
        except AttributeError:
            cls_module = cls.__module__
        else:
            cls_module = import_context


        result = type(cls)(name, (cls,), type(cls).__prepare__(name, (cls,)))

        result.__module__ = cls_module

        nodecopy = copy.copy(node)
        nodecopy.tags = copy.copy(nodecopy.tags)
        nodecopy.tag = nodecopy.tags.pop()

        data = self.construct_object(nodecopy)

        context = lang_context.SourceContext.from_object(node)
        if context is None:
            context = self._get_source_context(node, self.document_context)

        result.prepare_class(context, data)

        yield result

    def construct_python_object(self, classname, node):
        cls = self._get_class_from_tag(classname, node, 'object')
        if not issubclass(cls, lang_base.Object):
            raise yaml.constructor.ConstructorError(
                    "while constructing a Python object", node.start_mark,
                    "expected %s to be a subclass of importkit.meta.Object" % classname, node.start_mark)

        context = lang_context.SourceContext.from_object(node)
        if context is None:
            context = self._get_source_context(node, self.document_context)

        nodecopy = copy.copy(node)
        nodecopy.tags = copy.copy(nodecopy.tags)
        nodecopy.tag = nodecopy.tags.pop()

        data = self.construct_object(nodecopy, True)

        newargs = ()
        newkwargs = {}

        try:
            getnewargs = cls.__sx_getnewargs__
        except AttributeError:
            pass
        else:
            newargs = getnewargs(context, data)
            if not isinstance(newargs, tuple):
                newargs, newkwargs = newargs['args'], newargs['kwargs']

        result = cls.__new__(cls, *newargs, **newkwargs)
        lang_context.SourceContext.register_object(result, context)

        yield result

        try:
            constructor = type(result).__sx_setstate__
        except AttributeError:
            pass
        else:
            constructor(result, data)

    def construct_ordered_mapping(self, node, deep=False, populate_namespace=False):
        if isinstance(node, yaml.nodes.MappingNode):
            self.flatten_mapping(node)

        if not isinstance(node, yaml.nodes.MappingNode):
            raise yaml.constructor.ConstructorError(None, None,
                    "expected a mapping node, but found %s" % node.id,
                    node.start_mark)

        mapping = []
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, collections.Hashable):
                raise yaml.constructor.ConstructorError("while constructing a mapping",
                                                        node.start_mark,
                                                        "found unhashable key", key_node.start_mark)

            if self._is_object_or_class(value_node):
                value_context = self._get_source_context(value_node, self.document_context)
                lang_context.SourceContext.register_object(value_node, value_context)
                value_context.mapping_key = key

            value = self.construct_object(value_node, deep=deep)
            mapping.append((key, value))

            if populate_namespace:
                self.document_context.namespace[key] = value

        return mapping

    def construct_ordered_map(self, node):
        data = collections.OrderedDict()
        yield data
        value = self.construct_ordered_mapping(node)
        data.update(value)

    def construct_multimap(self, node):
        data = []
        yield data
        value = self.construct_ordered_mapping(node)
        data.extend(value)

    def construct_frozenset(self, node):
        value = self.construct_mapping(node)
        return frozenset(value)

    def construct_decimal(self, node):
        value = self.construct_scalar(node)
        return decimal.Decimal(value)

    def construct_namespace_map(self, node):
        data = collections.OrderedDict()
        yield data
        return self.construct_ordered_mapping(node, populate_namespace=True)

    def construct_python_expression(self, node):
        if not isinstance(node.value, str):
            raise yaml.constructor.ConstructorError("while constructing a python expression",
                                                    node.start_mark,
                                                    "found a non-string node", node.start_mark)

        try:
            result = compile(node.value, '<string>', 'exec', ast.PyCF_ONLY_AST)
        except (SyntaxError, TypeError) as e:
            raise yaml.constructor.ConstructorError("while constructing a python expression",
                                                    node.start_mark,
                                                    "syntax error", node.start_mark) from e
        else:
            result.source = node.value
            return result

    def construct_moduleclass_tag(self, node):
        if not isinstance(node.value, str):
            raise yaml.constructor.ConstructorError("while constructing module tag",
                                                    node.start_mark,
                                                    "found a non-string node", node.start_mark)

        return ModuleTag(node.value)


Constructor.add_multi_constructor(
    'tag:importkit.magic.io,2009/importkit/class/derive:',
    Constructor.construct_python_class
)

Constructor.add_multi_constructor(
    'tag:importkit.magic.io,2009/importkit/object/create:',
    Constructor.construct_python_object
)

Constructor.add_constructor(
    'tag:importkit.magic.io,2009/importkit/orderedmap',
    Constructor.construct_ordered_map
)

Constructor.add_constructor(
    'tag:importkit.magic.io,2009/importkit/multimap',
    Constructor.construct_multimap
)

Constructor.add_constructor(
    'tag:importkit.magic.io,2009/importkit/frozenset',
    Constructor.construct_frozenset
)

Constructor.add_constructor(
    'tag:importkit.magic.io,2009/importkit/decimal',
    Constructor.construct_decimal
)

Constructor.add_constructor(
    'tag:importkit.magic.io,2009/importkit/schema/namespace',
    Constructor.construct_namespace_map
)

Constructor.add_constructor(
    '!tpl',
    lambda loader, node: Template(node.value)
)

Constructor.add_constructor(
    '!python',
    Constructor.construct_python_expression
)

Constructor.add_constructor(
    '!module',
    Constructor.construct_moduleclass_tag
)
