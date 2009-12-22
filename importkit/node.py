class NodeSourcePoint(object):
    def __init__(self, line, column, pointer):
        self.line = line
        self.column = column
        self.pointer = pointer


class NodeSourceContext(object):
    def __init__(self, name, buffer, start, end):
        self.name = name
        self.buffer = buffer
        self.start = start
        self.end = end


class Node(object):
    def __init__(self, value, context):
        self.value = value
        self.context = context
