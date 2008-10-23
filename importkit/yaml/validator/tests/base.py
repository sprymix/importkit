import unittest, os, yaml

from semantix.lib import validator, readers

__all__ = ['failUnlessException', 'failUnlessResult', 'SchemaTest']

def failUnlessException(ex_cls, ex_msg):
    def dec(func):
        def new(*args, **kwargs):
            slf = args[0]

            error = None
            try:
                slf.schema.check(slf.load(func.__doc__))
            except ex_cls, error:
                error = str(error)

            slf.failUnless(error is not None and ex_msg in error, 'expected error "%s" got "%s" instead' % (ex_msg, error))
        return new
    return dec

def failUnlessResult(expected_result=None, key=None, value=None):
    def dec(func):
        def new(*args, **kwargs):
            slf = args[0]

            error = None
            try:
                result = slf.schema.check(slf.load(func.__doc__))
            except Exception, error:
                error = str(error)
            else:
                if key is None:
                    slf.failUnless(expected_result == result, 'unexpected validation result %r, expected %r' %
                                                              (result, expected_result))
                else:
                    slf.failUnless(result[key] == value, 'unexpected validation result %r, expected %r' %
                                                              (result[key], value))


            slf.failUnless(error is None, 'unexpected error: ' + str(error))
        return new
    return dec

class SchemaTest(unittest.TestCase):
    def load(self, str):
        return yaml.load(str)

    def get_schema(self, file):
        return validator.Schema(readers.read(os.path.join(os.path.dirname(__file__), file)))
