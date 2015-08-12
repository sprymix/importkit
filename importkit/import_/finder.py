##
# Copyright (c) 2008-2014 Sprymix Inc.
# All rights reserved.
#
# See LICENSE for details.
##


from importlib import machinery

from importlib import _bootstrap

try:
    from importlib import _bootstrap_external
except ImportError:
    from importlib import _bootstrap as _bootstrap_external


import os
import sys


def _get_file_loaders():
    from importkit.meta import LanguageMeta

    loader_details = list(_bootstrap_external._get_supported_file_loaders())

    lang_loaders = list(LanguageMeta.get_loaders())
    ext_map = {}

    for loader, extensions in lang_loaders:
        for extension in extensions:
            ext_map[extension] = loader

    for i, (loader, extensions) in enumerate(loader_details):
        untouched_exts = set(extensions) - set(ext_map)
        loader_details[i] = (loader, list(untouched_exts))

    loader_details.extend(lang_loaders)

    return loader_details


class FileFinder(machinery.FileFinder):
    def __init__(self, path, *details):
        super().__init__(path, *details)

    @classmethod
    def update_loaders(cls, finder, loader_details, replace=False):
        loaders = []

        for loader, suffixes in loader_details:
            loaders.extend((s, loader) for s in suffixes)

        finder._loaders[:] = loaders

        finder.invalidate_caches()

    @classmethod
    def path_hook(cls):
        def path_hook_for_FileFinder(path):
            return cls(path, *_get_file_loaders())
        return path_hook_for_FileFinder

    def __repr__(self):
        return 'mm.FileFinder({!r})'.format(self.path)


def install():
    for i, hook in enumerate(sys.path_hooks):
        hook_mod = getattr(hook, '__module__', '')
        if (hook_mod.startswith('importlib')
                or hook_mod.startswith('_frozen_importlib')):
            sys.path_hooks.insert(i, FileFinder.path_hook())
            break
    else:
        sys.path_hooks.insert(0, FileFinder.path_hook())


_packages = set()


def update_finders():
    loader_details = _get_file_loaders()
    for path, finder in list(sys.path_importer_cache.items()):
        if isinstance(finder, FileFinder) or is_importkit_path(path):
            FileFinder.update_loaders(finder, loader_details,
                                      isinstance(finder, FileFinder))


def register_package(package_name):
    global _packages

    _packages.add(package_name)


def is_importkit_path(path):
    rpath = os.path.realpath

    for pkgname in _packages:
        pkg = sys.modules.get(pkgname)
        if pkg:
            if any(rpath(path) == rpath(nspath) for nspath in pkg.__path__):
                return True
    else:
        return False


register_package('importkit')
