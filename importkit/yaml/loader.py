import yaml
import importlib

import semantix.lang.meta
from semantix.utils.type_utils import ClassFactory


class AttributeMappingNode(yaml.nodes.MappingNode):
    @classmethod
    def from_map_node(cls, node):
        result = cls(tag=node.tag, value=node.value, start_mark=node.start_mark, end_mark=node.end_mark,
                     flow_style=node.flow_style)
        if hasattr(node, 'tags'):
            result.tags = node.tags
        return result


class Scanner(yaml.scanner.Scanner):

    def __init__(self):
        super().__init__()
        self.alnum_range = self.mcrange([('0', '9'), ('a', 'z'), ('A', 'Z')]) + ['_']

    def mcrange(self, ranges):
        result = []
        for c1, c2 in ranges:
            result.extend(self.crange(c1, c2))
        return result

    def crange(self, c1, c2):
        return [chr(o) for o in range(ord(c1), ord(c2))]

    def scan_directive(self):
        start_mark = self.get_mark()

        directives = {
            '%SCHEMA': self.alnum_range + ['.'],
            '%NAME': self.alnum_range
        }

        for directive, charrange in directives.items():
            if self.prefix(len(directive)) == directive:
                self.forward()
                name = self.scan_directive_name(start_mark)
                value = self.scan_string(start_mark, charrange)
                end_mark = self.get_mark()
                self.scan_directive_ignored_line(start_mark)
                return yaml.tokens.DirectiveToken(name, value, start_mark, end_mark)
        else:
            return super().scan_directive()

    def scan_string(self, start_mark, allowed_range):
        while self.peek() == ' ':
            self.forward()
        length = 0
        ch = self.peek(length)
        while ch in allowed_range:
            length += 1
            ch = self.peek(length)
        if not length:
            raise yaml.scanner.ScannerError("while scanning a directive", start_mark,
                    "expected alphabetic or numeric character, but found %r"
                    % ch, self.get_mark())
        value = self.prefix(length)
        self.forward(length)
        ch = self.peek()
        if ch not in '\0 \r\n\x85\u2028\u2029':
            raise yaml.scanner.ScannerError("while scanning a directive", start_mark,
                    "expected alphabetic or numeric character, but found %r"
                    % ch, self.get_mark())
        return value

    def push_tokens(self, tokens):
        self.tokens[0:0] = tokens


class Parser(yaml.parser.Parser):
    def process_directives(self):
        self.schema = None
        self.document_name = None

        rejected_tokens = []

        while self.check_token(yaml.tokens.DirectiveToken):
            token = self.get_token()
            if token.name == 'SCHEMA':
                if self.schema:
                    raise yaml.parser.ParserError(None, None, "duplicate SCHEMA directive", token.start_mark)
                self.schema = token.value
            elif token.name == 'NAME':
                if self.document_name:
                    raise yaml.parser.ParserError(None, None, "duplicate NAME directive", token.start_mark)
                self.document_name = token.value
            else:
                rejected_tokens.append(token)

        self.push_tokens(rejected_tokens)

        return super().process_directives()

    def parse_document_start(self):
        event = super().parse_document_start()
        if isinstance(event, yaml.events.DocumentStartEvent):
            event.schema = self.schema
            event.document_name = self.document_name

        return event


class Composer(yaml.composer.Composer):
    def compose_document(self):
        start_document = self.get_event()

        node = self.compose_node(None, None)

        schema = getattr(start_document, 'schema', None)
        if schema:
            module, obj = schema.rsplit('.', 1)
            module = importlib.import_module(module)
            schema = getattr(module, obj)
            node = schema().check(node)

        node.document_name = getattr(start_document, 'document_name', None)

        self.get_event()
        self.anchors = {}
        self.schema = None
        return node


class Constructor(yaml.constructor.Constructor):
    def __init__(self, context=None):
        super().__init__()
        self.loading_context = context

    def _get_class_from_tag(self, clsname, node, intent='class'):
        if not clsname:
            raise yaml.constructor.ConstructorError("while constructing a Python %s" % intent, node.start_mark,
                                                    "expected non-empty class name appended to the tag", node.start_mark)

        module_name, class_name = clsname.rsplit('.', 1)

        try:
            module = importlib.import_module(module_name)
        except ImportError as exc:
            raise yaml.constructor.ConstructorError("while constructing a Python %s" % intent, node.start_mark,
                                                    "could not find %r (%s)" % (module_name, exc), node.start_mark)

        return getattr(module, class_name)

    def _get_source_context(self, node, loading_context):
        start = semantix.lang.meta.SourcePoint(node.start_mark.line, node.start_mark.column,
                                               node.start_mark.pointer)
        end = semantix.lang.meta.SourcePoint(node.end_mark.line, node.end_mark.column,
                                               node.end_mark.pointer)

        module = loading_context.module if loading_context is not None else None
        context = semantix.lang.meta.SourceContext(node.start_mark.name, node.start_mark.buffer,
                                                   start, end, module)
        return context

    def construct_python_class(self, parent, node):
        cls = self._get_class_from_tag(parent, node, 'class')
        name = getattr(node, 'document_name', cls.__name__ + '_' + str(id(node)))
        result = ClassFactory(name, (cls,), {})
        result.__module__ = cls.__module__

        data = self.construct_mapping(node, deep=True)
        result.init_class(data)

        return result

    def construct_python_object(self, classname, node):
        cls = self._get_class_from_tag(classname, node, 'object')
        if not issubclass(cls, semantix.lang.meta.Object):
            raise yaml.constructor.ConstructorError(
                    "while constructing a Python object", node.start_mark,
                    "expected %s to be a subclass of semantix.lang.meta.Object" % classname, node.start_mark)

        node.tag = node.tags.pop()
        del self.recursive_objects[node]
        data = self.construct_object(node, True)
        self.recursive_objects[node] = None

        context = self._get_source_context(node, self.loading_context)

        return cls.construct(data, context)

    def get_dict(self):
        # Construct and return the next document.
        if self.check_node():
            node = self.get_node()
            data = self.construct_document(node)

            if isinstance(node, AttributeMappingNode):
                for d in data.items():
                    yield d
            else:
                yield (node.document_name, data)


Constructor.add_multi_constructor(
    'tag:semantix.sprymix.com,2009/semantix/class/derive:',
    Constructor.construct_python_class
)

Constructor.add_multi_constructor(
    'tag:semantix.sprymix.com,2009/semantix/object/create:',
    Constructor.construct_python_object
)


class Loader(yaml.reader.Reader, Scanner, Parser, Composer, Constructor, yaml.resolver.Resolver):
    def __init__(self, stream, context=None):
        yaml.reader.Reader.__init__(self, stream)
        Scanner.__init__(self)
        Parser.__init__(self)
        Composer.__init__(self)
        Constructor.__init__(self, context)
        yaml.resolver.Resolver.__init__(self)
