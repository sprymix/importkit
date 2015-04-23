##
# Copyright (c) 2008-2012 Sprymix Inc.
# All rights reserved.
#
# See LICENSE for details.
##


import importlib
import unittest

from importkit import context as lang_context
from importkit.yaml import exceptions as yaml_errors


class TestLangImport(unittest.TestCase):
    def test_utils_lang_yaml_import(self):
        modname = 'importkit.yaml.tests.testdata.test_import'
        mod = importlib.import_module(modname)
        self.assertTrue(
            hasattr(mod, 'SimpleImport') and
            mod.SimpleImport['attr1'] == 'test')

    def test_utils_lang_yaml_module_import(self):
        modname = 'importkit.yaml.tests.testdata.test_module_import'
        mod = importlib.import_module(modname)
        self.assertTrue(
            hasattr(mod, 'attr1') and hasattr(mod, 'attr2') and
            hasattr(mod, 'attr3'))

    def test_utils_lang_yaml_module_import_bad1(self):
        modname = 'importkit.yaml.tests.testdata.test_module_import_bad1'
        err = 'unexpected document after module-level schema document'
        with self.assertRaises(yaml_errors.YAMLCompositionError, msg=err):
            importlib.import_module(modname)

    def test_utils_lang_yaml_module_import_bad2(self):
        modname = 'importkit.yaml.tests.testdata.test_module_import_bad2'
        err = 'unexpected module-level schema document'
        with self.assertRaises(yaml_errors.YAMLCompositionError, msg=err):
            importlib.import_module(modname)

    @unittest.expectedFailure
    def test_utils_lang_yaml_ambiguous_import(self):
        with self.assertRaises(ImportError):
            from importkit.yaml.tests.testdata.ambig import test

    def test_utils_lang_yaml_module_import_import(self):
        modname = 'importkit.yaml.tests.testdata.test_module_import_import'
        importlib.import_module(modname)

    def test_utils_lang_yaml_moduleclass_tag(self):
        modname = 'importkit.yaml.tests.testdata.test_modclass_tag'
        mod = importlib.import_module(modname)
        from .testdata import modclass
        self.assertTrue(isinstance(mod, modclass.CustomModuleClass))
