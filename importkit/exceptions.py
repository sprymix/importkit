##
# Copyright (c) 2013, 2015 Sprymix Inc.
# All rights reserved.
#
# See LICENSE for details.
##


try:
    from metamagic.utils import markup
    markup_support = True
except ImportError:
    markup_support = False


try:
    from metamagic import exceptions as mm_exceptions
except ImportError as e:
    BaseError = Exception
    metamagic_error = False
else:
    BaseError = mm_exceptions.MetamagicError
    metamagic_error = True


if markup_support:
    class SourceErrorContext(markup.MarkupExceptionContext):
        def __init__(self, source_context):
            self.source_context = source_context

        @classmethod
        def as_markup(cls, self, *, ctx):
            me = markup.elements

            if self.source_context:
                tbp = me.lang.TracebackPoint(
                    name=self.source_context.name,
                    lineno=self.source_context.start.line,
                    filename=self.source_context.filename or '<unknown>')

                tbp.load_source(lines=self.source_context.buffer)
            else:
                tbp = me.doc.Text(text='Unknown source context')

            return me.lang.ExceptionContext(title=self.title, body=[tbp])


class LanguageError(BaseError):
    def __init__(self, msg, *, context=None, hint=None, **kwargs):
        if metamagic_error:
            if not hint and context:
                hint = 'Fix the {!r} module (line: ~{})'.format(
                    context.name, context.start.line)

            super().__init__(msg, hint=hint, **kwargs)

            if markup_support:
                mm_exceptions._add_context(
                    self, SourceErrorContext(source_context=context))
        else:
            super().__init__(msg)


class UnresolvedError(LanguageError):
    pass


class DefinitionError(LanguageError):
    pass
