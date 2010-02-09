##
# Copyright (c) 2008-2010 Sprymix Inc.
# All rights reserved.
#
# See LICENSE for details.
##


import os
import yaml
from semantix.lang import meta
from semantix.lang.yaml import loader


class Language(meta.Language):
    @classmethod
    def recognize_file(cls, filename, try_append_extension=False):
        if try_append_extension and os.path.exists(filename + '.yml'):
            return filename + '.yml'
        elif os.path.exists(filename) and filename.endswith('.yml'):
            return filename

    @classmethod
    def load(cls, stream, context=None):
        if not context:
            context = meta.DocumentContext()

        ldr = loader.Loader(stream, context)
        while ldr.check_data():
            yield ldr.get_data()


    @classmethod
    def load_dict(cls, stream, context=None):
        if not context:
            context = meta.DocumentContext()

        ldr = loader.Loader(stream, context)
        for d in ldr.get_dict():
            yield d
