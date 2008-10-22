__all__ = ['failUnlessException']

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
