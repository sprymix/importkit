from semantix.lib.validator import types, error

class Schema(object):
    def __init__(self, dct, resource_name=''):
        self.refs = {}
        self.__dct = dct
        self.root = None
        self.resource_name = resource_name


    def _build(self, dct):
        dct_id = id(dct)
        dct_type = dct['type']

        if dct_id in self.refs:
            return self.refs[dct_id]

        if dct_type == 'choice':
            tp = types.ChoiceType(self)
        elif dct_type == 'map':
            tp = types.MappingType(self)
        elif dct_type == 'seq':
            tp = types.SequenceType(self)
        elif dct_type == 'str':
            tp = types.StringType(self)
        elif dct_type == 'int':
            tp = types.IntType(self)
        elif dct_type == 'float':
            tp = types.FloatType(self)
        elif dct_type == 'number':
            tp = types.NumberType(self)
        elif dct_type == 'text':
            tp = types.TextType(self)
        elif dct_type == 'any':
            tp = types.AnyType(self)
        elif dct_type == 'bool':
            tp = types.BoolType(self)
        else:
            raise error.SchemaError('unknown type: ' + dct_type)


        self.refs[dct_id] = tp

        tp.load(dct)
        return tp


    def check(self, data):
        if self.root is None:
            self.root = self._build(self.__dct)
            del self.__dct

        return self.root.check(data, '')
