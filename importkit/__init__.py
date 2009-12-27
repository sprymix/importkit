import yaml
import sys
import os
import imp
from importlib import abc
import collections

from semantix.lang.meta import LanguageMeta
import semantix.lang.yaml


class SemantixLangLoaderError(Exception):
    pass


class Importer(abc.Finder, abc.Loader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.module_file_map = dict()

    def _locate_module_file(self, fullname, path):
        prefix, basename = fullname.rsplit('.', 1)

        for p in path:
            test = os.path.join(p, basename)
            result = LanguageMeta.recognize_file(test, True)
            if result:
                return result

    def find_module(self, fullname, path=None):
        if path:
            result = self._locate_module_file(fullname, path)
            if result:
                self.module_file_map[fullname] = result
                return self

    def load_module(self, fullname):
        if fullname in sys.modules:
            return sys.modules[fullname]

        language, filename = self.module_file_map[fullname]

        new_mod = imp.new_module(fullname)
        setattr(new_mod, '__file__', filename)
        setattr(new_mod, '__path__', os.path.dirname(filename))
        setattr(new_mod, '__odict__', collections.OrderedDict())

        sys.modules[fullname] = new_mod

        with open(filename) as stream:
            try:
                attributes = language.load_dict(stream)
            except Exception as error:
                raise ImportError('unable to import "%s" (%s)' % (fullname, error))

            for attribute_name, attribute_value in attributes:
                if attribute_name:
                    new_mod.__odict__[attribute_name] = attribute_value
                    setattr(new_mod, attribute_name, attribute_value)

        return new_mod


def load(filename):
    (lang, filename) = LanguageMeta.recognize_file(filename)
    if lang:
        with open(filename) as f:
            result = lang.load(f)
            for d in result:
                yield d

        return

    raise SemantixLangLoaderError('unable to load file:  %s' % filename)
