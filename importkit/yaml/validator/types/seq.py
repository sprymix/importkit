from .base import SchemaType
from ..error import SchemaValidationError

class SequenceType(SchemaType):
    __slots__ = ['sequence_type']

    def __init__(self, schema):
        super(SequenceType, self).__init__(schema)
        self.sequence_type = None

    def load(self, dct):
        super(SequenceType, self).load(dct)

        self.sequence_type = self.schema._build(dct['sequence'][0])

    def check(self, data, path):
        super(SequenceType, self).check(data, path)

        if not isinstance(data, list):
            raise SchemaValidationError('list expected', path)

        self.sequence_type.begin_checks()
        for i in xrange(0, len(data)):
            data[i] = self.sequence_type.check(data[i], path + '/' + str(i))
        self.sequence_type.end_checks()

        return data
