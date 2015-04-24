##
# Copyright (c) 2008-2010, 2013 Sprymix Inc.
# All rights reserved.
#
# See LICENSE for details.
##


import marshal
import os
import sys
try:
    from importlib._bootstrap import _SourceFileLoader
except ImportError:
    from importlib._bootstrap import SourceFileLoader as _SourceFileLoader

from importlib import _bootstrap, util as importlib_util

from importkit import meta as lang_meta, loader as lang_loader
from importkit import runtimes as lang_runtimes
from importkit.import_ import utils as imputils
from importkit.import_ import loader as imploader
from . import utils as pyutils
from ..import_ import cache as caches


class LangModuleCache(lang_loader.LangModuleCache):
    @property
    def metainfo_path(self):
        path = self.path
        path += '.metainfo'
        return path

    def unmarshal_code(self, code_bytes):
        return marshal.loads(code_bytes[12:])


class Loader(imploader.LoaderCommon, _SourceFileLoader, imploader.SourceLoader,
             lang_loader.LanguageLoaderBase, imploader.LoaderIface):
    def __init__(self, fullname, filename, language):
        super().__init__(fullname, filename)
        self._language = language
        self._imports = {}

    def create_cache(self, modname):
        return LangModuleCache(modname, self)

    def process_code(self, modname, code, cache):
        import_stmts = pyutils.get_top_level_imports(code)
        package = modname if self.is_package(modname) else modname.rpartition('.')[0]
        imports = imputils.modules_from_import_statements(package, import_stmts,
                                                          ignore_missing=True)
        cache.metainfo.dependencies = imports

    def get_cache_path(self, modname):
        source_path = self.get_filename(modname)
        return imputils.cache_from_source(source_path)

    def get_code(self, fullname):
        code = super().get_code(fullname)

        if not self.is_deptracked(fullname):
            return code

        cache = self.create_cache(fullname)
        source_path = self.get_filename(fullname)

        if cache is not None:
            try:
                cache.validate()
            except ImportError:
                self.process_code(fullname, code, cache)

                if not sys.dont_write_bytecode:
                    try:
                        cache.dump()
                    except NotImplementedError:
                        pass

            self._imports[fullname] = cache.metainfo.dependencies

        return code

    def exec_module(self, module):
        super(_SourceFileLoader, self).exec_module(module)
        module = self._init_module(module)
        sys.modules[module.__name__] = module

    if sys.version_info[:2] < (3, 4):
        @importlib_util.module_for_loader
        def _load_module_wrapper(self, module, *, sourceless=False):
            name = module.__name__
            module.__file__ = self.get_filename(name)
            if not sourceless:
                try:
                    module.__cached__ = _bootstrap.cache_from_source(module.__file__)
                except NotImplementedError:
                    module.__cached__ = module.__file__
            else:
                module.__cached__ = module.__file__
            module.__package__ = name
            if self.is_package(name):
                module.__path__ = [_bootstrap._path_split(module.__file__)[0]]
            else:
                module.__package__ = module.__package__.rpartition('.')[0]
            module.__loader__ = self
            code_object = self.get_code(name)
            _bootstrap._call_with_frames_removed(exec, code_object, module.__dict__)
            return module
    else:
        def _load_module_wrapper(self, fullname):
            return _SourceFileLoader.load_module(self, fullname)

    def _load_module_impl(self, fullname):
        mod = self._load_module_wrapper(fullname)
        self._init_module(mod)
        return mod

    def _init_module(self, mod):
        fullname = mod.__name__

        try:
            track_policy = mod.__mm_track_dependencies__
        except AttributeError:
            tracked = self.is_deptracked(fullname)
        else:
            caches.deptracked_modules[mod.__name__] = track_policy
            tracked = track_policy

        try:
            module_class = mod.__sx_moduleclass__
        except AttributeError:
            pass
        else:
            _module = module_class(mod.__name__)
            _module.__dict__.update(mod.__dict__)
            mod = _module
            sys.modules[fullname] = mod

        if tracked:
            mod.__sx_imports__ = self._imports.get(fullname) or ()
            mod.__language__ = self._language

        modtags = self.get_modtags(fullname)
        if modtags:
            mod.__mm_module_tags__ = modtags

        return mod


class Language(lang_meta.Language):
    file_extensions = ('py',)
    loader = Loader


class PythonRuntime(lang_runtimes.LanguageRuntime, languages=Language, default=True):
    pass
