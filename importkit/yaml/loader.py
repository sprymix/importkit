##
# Copyright (c) 2008-2013 Sprymix Inc.
# All rights reserved.
#
# See LICENSE for details.
##


import yaml

from importkit.import_ import get_object, ObjectImportError
from importkit import context as lang_context
from importkit.yaml import constructor, parser
from importkit.yaml import exceptions as yaml_errors
from importkit.yaml import schema as yaml_schema


class Loader(yaml.reader.Reader, parser.Scanner, parser.Parser, constructor.Composer,
             constructor.Constructor, yaml.resolver.Resolver):
    def __init__(self, stream, context=None):
        yaml.reader.Reader.__init__(self, stream)
        parser.Scanner.__init__(self)
        parser.Parser.__init__(self)
        constructor.Composer.__init__(self)
        constructor.Constructor.__init__(self, context)
        yaml.resolver.Resolver.__init__(self)

        if context and context.module:
            # That's needed for 'yaml.Reader' class to raise exceptions with
            # correct filename
            self.name = context.module.__file__
            self.module_name = context.module.__name__

    def _wrap_yaml_error(self, ex):
        if isinstance(ex, yaml.MarkedYAMLError):
            ctx = None
            if ex.context_mark:
                ctx = ex.context_mark
            elif ex.problem_mark:
                ctx = ex.problem_mark

            if not ctx:
                return ex

            ex_ctx = lang_context.SourceContext(name=self.module_name,
                                                filename=ctx.name,
                                                start=lang_context.SourcePoint(line=ctx.line,
                                                                               column=ctx.column,
                                                                               pointer=None),
                                                end=None,
                                                buffer=None)

            new_ex = yaml_errors.YAMLError(str(ex), context=ex_ctx)
            new_ex.__suppress_context__ = True
            return new_ex

        return ex

    def get_dict(self):
        document_no = 0
        seen_module_schema = False

        while self.check_node():
            try:
                node = self.get_node()
            except yaml.YAMLError as ex:
                raise self._wrap_yaml_error(ex)

            data = self.construct_document(node)

            if node.schema is not None and issubclass(node.schema, yaml_schema.ModuleSchemaBase):
                if document_no > 0:
                    msg = 'unexpected module-level schema document'
                    details = ('Module-level schema document must be the first and only in each '
                               'YAML file.')
                    hint = 'Split documents into separate files.'
                    context = lang_context.SourceContext.from_object(node)
                    raise yaml_errors.YAMLCompositionError(msg, details=details, hint=hint,
                                                           context=context)
                try:
                    module_class = node.schema.get_module_class()
                except NotImplementedError:
                    module_class = None

                if module_class is not None:
                    yield ('__sx_moduleclass__', module_class)

                context = lang_context.SourceContext.from_object(node)

                yield ('__sx_yamlschema__', node.schema)

                if issubclass(node.schema, yaml_schema.NamespaceModuleSchemaBase):
                    for d in context.document.namespace.items():
                        yield d
                else:
                    for d in data.items():
                        yield d

                seen_module_schema = True
            else:
                if seen_module_schema:
                    msg = 'unexpected document after module-level schema document'
                    details = ('Module-level schema document must be the first and only in each '
                               'YAML file.')
                    hint = 'Split documents into separate files.'
                    context = lang_context.SourceContext.from_object(node)
                    raise yaml_errors.YAMLCompositionError(msg, details=details, hint=hint,
                                                           context=context)

                if document_no == 0:
                    # First document, check for module-level attributes
                    if isinstance(data, constructor.ModuleTag):
                        try:
                            modclass = get_object(str(data))
                        except ObjectImportError as e:
                            msg = 'could not find module class: {}'.format(data)
                            context = lang_context.SourceContext.from_object(node)
                            raise yaml_errors.YAMLCompositionError(msg, context=context) from e
                        else:
                            yield ('__sx_moduleclass__', modclass)

                yield (node.document_name, data)

            document_no += 1


class RecordingLoader(Loader):
    def _get_current_event(self):
        return self._current_event

    def _set_current_event(self, event):
        self._current_event = event
        if event is not None:
            self._eventlog.append(event)

            if isinstance(event, yaml.DocumentStartEvent):
                self._documents.append(event)

    current_event = property(_get_current_event, _set_current_event)

    def __init__(self, stream, context):
        super().__init__(stream, context)
        self._current_event = None
        self._eventlog = []
        self._documents = []
        self._loaded = False

    def _load(self):
        while self.check_event():
            self.get_event()

        self._loaded = True

    def get_code(self):
        if not self._loaded:
            try:
                self._load()
            except yaml.YAMLError as ex:
                raise self._wrap_yaml_error(ex)

        return self._eventlog

    def get_documents(self):
        if not self._loaded:
            self._load()

        return self._documents


class ReplayLoader(Loader):
    def __init__(self, eventlog, context):
        super().__init__('', context)
        self.state = self._next_event
        self.event_iterator = iter(eventlog)

    def _next_event(self):
        try:
            return next(self.event_iterator)
        except StopIteration:
            return None
