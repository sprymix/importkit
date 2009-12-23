import yaml
import importlib

from semantix.utils.type_utils import ClassFactory

class Scanner(yaml.scanner.Scanner):
    def scan_directive(self):
        start_mark = self.get_mark()

        if self.prefix(7) == '%SCHEMA':
            self.forward()
            name = self.scan_directive_name(start_mark)
            value = self.scan_schema_directive_value(start_mark)
            end_mark = self.get_mark()
            self.scan_directive_ignored_line(start_mark)
            return yaml.tokens.DirectiveToken(name, value, start_mark, end_mark)
        elif self.prefix(5) == '%NAME':
            self.forward()
            name = self.scan_directive_name(start_mark)
            value = self.scan_name_directive_value(start_mark)
            end_mark = self.get_mark()
            self.scan_directive_ignored_line(start_mark)
            return yaml.tokens.DirectiveToken(name, value, start_mark, end_mark)
        else:
            return super().scan_directive()

    def scan_schema_directive_value(self, start_mark):
        while self.peek() == ' ':
            self.forward()
        length = 0
        ch = self.peek(length)
        while '0' <= ch <= '9' or 'A' <= ch <= 'Z' or 'a' <= ch <= 'z' or ch in '-._':
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

    def scan_name_directive_value(self, start_mark):
        while self.peek() == ' ':
            self.forward()
        length = 0
        ch = self.peek(length)
        while '0' <= ch <= '9' or 'A' <= ch <= 'Z' or 'a' <= ch <= 'z' or ch in '-_':
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
        self.tokens.extend(tokens)


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
    def construct_python_class(self, parent, node):
        if not parent:
            raise yaml.constructor.ConstructorError("while constructing a Python class", node.start_mark,
                                                    "expected non-empty name appended to the tag", node.start_mark)

        module_name, class_name = parent.rsplit('.', 1)

        try:
            module = importlib.import_module(module_name)
        except ImportError as exc:
            raise yaml.constructor.ConstructorError("while constructing a Python class", node.start_mark,
                                                    "could not find %r (%s)" % (module_name, exc), node.start_mark)

        cls = getattr(module, class_name)

        name = getattr(node, 'document_name', class_name + '_' + str(id(node)))
        result = ClassFactory(name, (cls,), {})
        result.__module__ = module_name

        data = self.construct_mapping(node, deep=True)
        result.init_class(data)

        return result

    def get_data(self):
        # Construct and return the next document.
        if self.check_node():
            node = self.get_node()
            return (node.document_name, self.construct_document(node))

    def get_single_data(self):
        # Ensure that the stream contains a single document and construct it.
        node = self.get_single_node()
        if node is not None:
            return (node.document_name, self.construct_document(node))
        return None


Constructor.add_multi_constructor(
    'tag:semantix.sprymix.com,2009/semantix/class/derive:',
    Constructor.construct_python_class
)


class Loader(yaml.reader.Reader, Scanner, Parser, Composer, Constructor, yaml.resolver.Resolver):
    def __init__(self, stream):
        yaml.reader.Reader.__init__(self, stream)
        Scanner.__init__(self)
        Parser.__init__(self)
        Composer.__init__(self)
        Constructor.__init__(self)
        yaml.resolver.Resolver.__init__(self)
