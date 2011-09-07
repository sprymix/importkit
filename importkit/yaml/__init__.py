##
# Copyright (c) 2008-2010 Sprymix Inc.
# All rights reserved.
#
# See LICENSE for details.
##


import os
import yaml
from semantix.utils.lang import meta, context as lang_context
from semantix.utils.lang.yaml import loader, dumper
from semantix.utils.functional import Adapter


class Language(meta.Language):
    file_extensions = ('yml',)

    @classmethod
    def load(cls, stream, context=None):
        if not context:
            context = lang_context.DocumentContext()

        ldr = loader.Loader(stream, context)
        while ldr.check_data():
            yield ldr.get_data()

    @classmethod
    def dump(cls, data):
        return yaml.dump(data, Dumper=dumper.Dumper)

    @classmethod
    def load_dict(cls, stream, context=None):
        if not context:
            context = lang_context.DocumentContext()

        ldr = loader.Loader(stream, context)
        for d in ldr.get_dict():
            yield d

    @classmethod
    def load_code(cls, stream, context=None):
        if not context:
            context = lang_context.DocumentContext()

        ldr = loader.RecordingLoader(stream, context)
        return ldr.get_code()

    @classmethod
    def execute_code(cls, code, context=None):
        if not context:
            context = lang_context.DocumentContext()

        ldr = loader.ReplayLoader(code, context)
        for d in ldr.get_dict():
            yield d


class ObjectMeta(Adapter):
    def __new__(metacls, name, bases, clsdict, *, adapts=None, ignore_aliases=False):
        result = super(ObjectMeta, metacls).__new__(metacls, name, bases, clsdict, adapts=adapts)
        result._adapts = adapts

        if ignore_aliases:
            dumper.Dumper.add_ignore_aliases(adapts if adapts is not None else result)

        return result

    def __init__(cls, name, bases, clsdict, *, adapts=None, ignore_aliases=False):
        super(ObjectMeta, cls).__init__(name, bases, clsdict, adapts=adapts)

        if hasattr(cls, '__sx_getstate__'):
            representer = lambda dumper, data: cls.represent_wrapper(data, dumper)

            if cls._adapts is not None:
                yaml.add_multi_representer(cls._adapts, representer, Dumper=dumper.Dumper)
            else:
                yaml.add_multi_representer(cls, representer, Dumper=dumper.Dumper)

    def get_adaptee(cls):
        return cls._adapts


class Object(meta.Object, metaclass=ObjectMeta):
    @classmethod
    def represent_wrapper(cls, data, dumper):
        result = cls.__sx_getstate__(data)

        if isinstance(result, dict):
            return dumper.represent_mapping('tag:yaml.org,2002:map', result)
        elif isinstance(result, list):
            return dumper.represent_sequence('tag:yaml.org,2002:seq', result)
        elif isinstance(result, str):
            return dumper.represent_scalar('tag:yaml.org,2002:str', result)
        elif isinstance(result, bool):
            return dumper.represent_scalar('tag:yaml.org,2002:bool', str(result))
        elif isinstance(result, int):
            return dumper.represent_scalar('tag:yaml.org,2002:int', str(result))
        else:
            assert False, 'unhandled representer result type: %s' % result
