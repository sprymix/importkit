import sys
import os
import imp
from importlib import abc
import collections

from semantix.lang.meta import LanguageMeta, DocumentContext


class ImportContext(str):
    def __getitem__(self, key):
        result = super().__getitem__(key)
        return self.__class__.copy(result, self)

    @classmethod
    def copy(cls, name, other):
        return cls(name)

    @classmethod
    def from_parent(cls, name, parent):
        return cls(name)


class Importer(abc.Finder, abc.Loader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.module_file_map = dict()

    def _locate_module_file(self, fullname, path):
        basename = fullname.rpartition('.')[2]

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

        context = DocumentContext(module=new_mod, import_context=fullname)

        with open(filename) as stream:
            try:
                attributes = language.load_dict(stream, context=context)
            except Exception as error:
                raise ImportError('unable to import "%s" (%s)' % (fullname, error))

            for attribute_name, attribute_value in attributes:
                attribute_name = str(attribute_name)
                new_mod.__odict__[attribute_name] = attribute_value
                setattr(new_mod, attribute_name, attribute_value)

        return new_mod
