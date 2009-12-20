import os
import yaml
from semantix import validator, readers


def raises(ex_cls, ex_msg):
    def dec(func):
        def new(*args, **kwargs):
            slf = args[0]

            error = None
            try:
                slf.schema.check(slf.load(func.__doc__))
            except ex_cls as ee:
                error = ee
                error = str(error)

            assert error is not None and ex_msg in error, \
                   'expected error "%s" got "%s" instead' % (ex_msg, error)
        return new
    return dec


def result(expected_result=None, key=None, value=None):
    def dec(func):
        def new(*args, **kwargs):
            slf = args[0]

            error = None
            try:
                result = slf.schema.check(slf.load(func.__doc__))
            except Exception as error:
                error = str(error)
            else:
                if key is None:
                    assert expected_result == result, \
                           'unexpected validation result %r, expected %r' % (result, expected_result)
                else:
                    assert result[key] == value, \
                           'unexpected validation result %r, expected %r' % (result[key], value)

            assert error is None, 'unexpected error: ' + str(error)
        return new
    return dec


class SchemaTest(object):
    def load(self, str):
        return yaml.load(str)

    @staticmethod
    def get_schema(file):
        return validator.Schema(readers.read(os.path.join(os.path.dirname(__file__), file)))
