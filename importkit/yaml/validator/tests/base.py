import os
from semantix import lang
from semantix.lang.yaml import loader
from semantix.utils.type_utils import ClassFactory


def raises(ex_cls, ex_msg):
    def dec(func):
        def new(*args, **kwargs):
            slf = args[0]

            constructor = loader.Constructor()
            try:
                node = slf.load(func.__doc__)
                node = slf.schema.check(node)
                constructor.construct_document(node)
            except ex_cls as ee:
                assert ex_msg in str(ee), \
                       'expected error "%s" got "%s" instead' % (ex_msg, ee)
            else:
                assert False, 'expected error "%s" got None instead' % ex_msg

        new.__name__ = func.__name__
        new.__doc__ = func.__doc__
        new.__dict__.update(func.__dict__)
        return new
    return dec


def result(expected_result=None, key=None, value=None):
    def dec(func):
        def new(*args, **kwargs):
            slf = args[0]

            constructor = loader.Constructor()
            try:
                node = slf.load(func.__doc__)
                node = slf.schema.check(node)
                result = constructor.construct_document(node)
            except Exception:
                raise
            else:
                if key is None:
                    assert expected_result == result, \
                           'unexpected validation result %r, expected %r' % (result, expected_result)
                else:
                    assert result[key] == value, \
                           'unexpected validation result %r, expected %r' % (result[key], value)

        new.__name__ = func.__name__
        new.__doc__ = func.__doc__
        new.__dict__.update(func.__dict__)
        return new
    return dec


class SchemaTest(object):
    def load(self, str):
        return loader.Loader(str).get_single_node()

    @staticmethod
    def get_schema(file):
        schema = ClassFactory(file, (lang.yaml.validator.Schema,), {})
        schema_data = lang.load(os.path.join(os.path.dirname(__file__), file))
        schema.init_class(next(schema_data))
        return schema()
