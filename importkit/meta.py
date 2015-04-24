##
# Copyright (c) 2008-2013 Sprymix Inc.
# All rights reserved.
#
# See LICENSE for details.
##


import base64
import collections
import hashlib
import functools
import itertools
import logging
import os
import sys
import types

from importkit.utils import adapter, topological

from .exceptions import LanguageError
from . import loader as lang_loader
from .loader import LanguageSourceFileLoader
from .import_ import finder
from .runtimes import LanguageRuntimeMeta


class LanguageMeta(type):
    languages = []

    def __new__(cls, name, bases, dct, *, register=True):
        lang = super(LanguageMeta, cls).__new__(cls, name, bases, dct)
        if register:
            LanguageMeta.languages.append(lang)
            finder.update_finders()
            if lang.default_runtime is not None:
                LanguageRuntimeMeta.default_runtimes[lang] = lang.default_runtime
        return lang

    def __init__(cls, name, bases, dct, *, register=True):
        super().__init__(name, bases, dct)

    @staticmethod
    def recognize_file(filename, try_append_extension=False, is_package=False):
        result = None

        for lang in LanguageMeta.languages:
            file_ = lang.recognize_file(filename, try_append_extension, is_package)
            if file_:
                if result is not None:
                    raise ImportError('ambiguous module import: %s, languages in conflict: %s' % \
                                                (filename, (lang, result[0])))
                result = (lang, file_)

        return result

    def get_loader(cls):
        return cls.loader

    @classmethod
    def get_loaders(cls):
        for lang in LanguageMeta.languages:
            yield (functools.partial(lang.loader, language=lang),
                   ['.' + ext for ext in lang.file_extensions])


class Language(metaclass=LanguageMeta, register=False):
    loader = LanguageSourceFileLoader
    file_extensions = ()
    default_runtime = None

    @classmethod
    def get_proxy_module_cls(cls):
        return None

    @classmethod
    def recognize_file(cls, filename, try_append_extension=False, is_package=False):
        if is_package:
            filename = os.path.join(filename, '__init__')

        if try_append_extension:
            for ext in cls.file_extensions:
                if os.path.exists(filename + '.' + ext):
                    return filename + '.' + ext

        elif os.path.exists(filename):
            for ext in cls.file_extensions:
                if filename.endswith('.' + ext):
                    return filename

    @classmethod
    def load_code(cls, stream, context):
        raise NotImplementedError

    @classmethod
    def execute_code(cls, code, context):
        raise NotImplementedError

    @classmethod
    def validate_code(cls, code):
        pass

    @classmethod
    def get_language_version(cls, metadata):
        return 0

    @classmethod
    def set_module_attributes(cls, module, attributes):
        module.__odict__ = collections.OrderedDict()

        for attribute_name, attribute_value in attributes:
            attribute_name = str(attribute_name)
            module.__odict__[attribute_name] = attribute_value
            setattr(module, attribute_name, attribute_value)


class ObjectError(Exception):
    def __init__(self, msg, context=None, code=None, note=None):
        self.msg = msg
        self.context = context
        self.code = code
        self.note = note

    def __str__(self):
        return self.msg


class Object:
    def __sx_setstate__(self, data):
        pass
