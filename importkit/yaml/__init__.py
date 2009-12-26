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
    def load(cls, stream):
        for d in yaml.load_all(stream, Loader=loader.Loader):
            yield d


    @classmethod
    def load_dict(cls, stream):
        ldr = loader.Loader(stream)
        for d in ldr.get_dict():
            yield d
